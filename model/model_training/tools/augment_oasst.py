"""
    Augment oasst dataset with sft generated results

    You can use augment new response using a model with bad response, ie non SFT model

    had to do this in a quick fashion, please tolerate the hackiness in the code

"""
import json
import os

# so far load_oasst_export is pretty deterministic in thread order
# means the train, val split stay the same
from model_training.custom_datasets.oasst_dataset import load_oasst_export
from model_training.models.reward_model import GPTNeoXRewardModel
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer


class AggregateResults:
    def __init__(self, reward_model) -> None:
        if "pythia" in reward_model:
            rank_model = GPTNeoXRewardModel.from_pretrained(reward_model)
        else:
            rank_model = AutoModelForSequenceClassification.from_pretrained(reward_model)
        self.rank_tokenizer = AutoTokenizer.from_pretrained(reward_model)
        self.rank_model = rank_model.half().cuda()

    def scoring(self, prefixes, answer):
        question = self.rank_tokenizer.sep_token.join(prefixes)
        inputs = self.rank_tokenizer(question, answer, return_tensors="pt").to(0)
        score = self.rank_model(**inputs).logits[0].cpu().detach()
        return score

    def aggregate(self, jsonl_filenames, dataset, split="val"):
        augmented = {}
        for train_augmented_filename in jsonl_filenames:
            with open(train_augmented_filename, "r") as f:
                for line in tqdm(f):
                    payload = json.loads(line)
                    idx = payload["idx"]
                    if idx not in augmented:
                        augmented[idx] = []
                    if len(payload["gen_samples"]) == 0:
                        continue
                    try:
                        scores = [
                            (float(self.scoring(payload["prefixes"], sample)), sample)
                            for sample in payload["gen_samples"]
                        ]
                        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
                        augmented[idx].append(sorted_scores[0][1])
                    except RuntimeError as e:
                        print(e)
                        continue

        with open(f"augmented_cycliric_oasst_2023-03-27_{split}.jsonl", "w") as f:
            for idx, payload in tqdm(enumerate(dataset), total=len(dataset), dynamic_ncols=True):
                output = {
                    "prefixes": payload[0],
                    "responses": payload[1],
                    "augmented": [],
                    "split": split,
                }
                if idx in augmented:
                    augmented = augmented[idx]
                    cleaned_aug = []
                    for a in augmented:
                        cleaned = (
                            a.replace("<|endoftext|>", "")
                            .replace("<|startoftoken|>human\n", "")
                            .replace("<human>", "")
                            .replace("<bot>", "")
                        )
                        cleaned_aug.append(cleaned)
                    output["augmented"] = cleaned_aug
                f.write(json.dumps(output) + "\n")


def r2_conversation(prefixes, tokenizer, model, top_k=10, temperature=0.7, max_new_tokens=512, model_name=""):
    text = ""
    for idx, convo in enumerate(prefixes):
        if idx % 2 == 0:
            text += "<|startoftoken|>human\n" + convo + "<|endoftoken|>"
        else:
            text += "<|startoftoken|>assistant\n" + convo + "<|endoftoken|>"
    input_text = text + "<|startoftoken|>assistant\n"
    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)

    generated_samples = []
    try:
        outputs = model.generate(
            **inputs,
            early_stopping=False,
            max_new_tokens=max_new_tokens,
            num_return_sequences=top_k,
            do_sample=True,
            temperature=temperature,
            pad_token_id=tokenizer.eos_token_id,
            # dialogue_collator.py line 36
        )
        gen_sequences = outputs.sequences[:, inputs["input_ids"].shape[-1] :]
        for output in gen_sequences:
            decoded = tokenizer.decode(
                output, truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"], skip_special_tokens=True
            )
            answer = decoded.split("<|endoftext|>")[0]
            if len(answer) > 0:
                generated_samples.append(answer)
    except RuntimeError as err:
        print(err)

    return generated_samples


def r0_conversation(prefixes, tokenizer, model, top_k=10, temperature=0.7, max_new_tokens=512, model_name=""):
    text = ""
    for idx, convo in enumerate(prefixes):
        if idx % 2 == 0:
            text += "<human>" + convo
        else:
            text += "<bot>" + convo + "<|endoftoken|>"
    input_text = text + "<bot>"
    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)

    generated_samples = []
    try:
        outputs = model.generate(
            **inputs,
            early_stopping=False,
            max_new_tokens=max_new_tokens,
            num_return_sequences=top_k,
            do_sample=True,
            temperature=temperature,
            pad_token_id=tokenizer.eos_token_id,
            # dialogue_collator.py line 36
        )
        gen_sequences = outputs.sequences[:, inputs["input_ids"].shape[-1] :]
        for output in gen_sequences:
            decoded = tokenizer.decode(
                output, truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"], skip_special_tokens=True
            )
            answer = decoded.split("<|endoftext|>")[0]
            if len(answer) > 0:
                generated_samples.append(answer)
    except RuntimeError as err:
        print(err)

    return generated_samples


def rallio_conversation(prefixes, tokenizer, model, top_k=2, temperature=0.7, max_new_tokens=512, model_name="Chip2"):
    name = "Chip2"
    if "Chip2" in model_name:
        name = "Chip2"
    elif "Kitt" in model_name:
        name = "Kitt"

    text = ""
    for idx, convo in enumerate(prefixes):
        if idx % 2 == 0:
            text += "User: " + convo + "\n"
        else:
            text += name + ": " + convo + "\n"
    input_text = text + name + ": "
    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)

    generated_samples = []
    try:
        outputs = model.generate(
            **inputs,
            early_stopping=False,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            num_return_sequences=top_k,
            top_p=0.95,
            temperature=0.5,
            penalty_alpha=0.6,
            output_scores=True,
            return_dict_in_generate=True,
            repetition_penalty=1.03,
            use_cache=True
            # dialogue_collator.py line 36
        )
        gen_sequences = outputs.sequences[:, inputs["input_ids"].shape[-1] :]
        for output in gen_sequences:
            decoded = tokenizer.decode(
                output, truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"], skip_special_tokens=True
            )
            answer = decoded.split("<|endoftext|>")[0]
            if len(answer) > 0:
                generated_samples.append(answer)
    except (RuntimeError, ValueError) as e:
        print(e)

    return generated_samples


def augment_conversation(model_name, dataset, split="train"):
    if "-r2" in model_name:  # OAI format
        chat_handler = r2_conversation
    elif "Rallio" in model_name:
        chat_handler = rallio_conversation
    else:  # <human>, <bot>
        chat_handler = r0_conversation
    chat_handler = r2_conversation

    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=".cache/").eval().half().cuda()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    output_file = "{}_2023-03-27-all_{}_{}.jsonl".format(model_name.replace("/", "-"), languages, split)
    added = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            for line in f:
                row = json.loads(line)
                added.add(row["idx"])
    with open(output_file, "a") as fout:
        for idx, row in tqdm(enumerate(dataset), total=len(dataset), dynamic_ncols=True):
            if idx in added:
                continue
            prefixes, answers = row
            samples = chat_handler(
                prefixes, tokenizer, model, temperature=0.1, top_k=8, max_new_tokens=256, model_name=model_name
            )
            fout.write(
                json.dumps({"prefixes": prefixes, "answers": answers, "gen_samples": samples, "idx": idx}) + "\n"
            )
            fout.flush()


if __name__ == "__main__":
    import glob

    # model_name = 'bigscience/bloom-560m'
    model_name = "theblackcat102/pythia-1b-deduped-sft"
    # latin_cyrillic
    languages = "bg,ca,cs,da,de,en,es,fr,hr,hu,it,nl,pl,pt,ro,ru,sl,sr,sv,uk"
    train, val = load_oasst_export(".cache/2023-03-27_oasst_research_all.jsonl.gz", lang=languages, mode="rm")

    print(len(train), len(val))
    augment_conversation(model_name, train, split="train")
    augment_conversation(model_name, val, split="val")

    agg = AggregateResults("theblackcat102/reward-model-deberta-v3-base-v2")
    agg.aggregate(glob.glob("*_val.jsonl"), val, "val")
    agg.aggregate(glob.glob("*_train.jsonl"), train, "train")
