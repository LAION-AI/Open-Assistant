import inspect
from typing import List, Tuple
import os
import json
import torch
import transformers
from custom_datasets.formatting import QA_SPECIAL_TOKENS
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DataCollatorWithPadding, PreTrainedTokenizer
from trlx.pipeline import BasePipeline, register_datapipeline
from trlx.trainer import register_trainer
from trlx.trainer.accelerate_ppo_trainer import AcceleratePPOTrainer
from trlx.models.modeling_ppo import AutoModelForCausalLMWithHydraValueHead
from huggingface_hub import hf_hub_download
# from trlx.utils.modeling import hf_get_causal_base_model, hf_get_hidden_size, hf_get_lm_head, make_head
from utils.utils import get_model


class CustomCausalLMHydraWithValueHead(AutoModelForCausalLMWithHydraValueHead):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_pretrained(  # noqa: max-complexity
        cls,
        config,
        tokenizer,
        kwargs=None,
        revision=None
    ):
        """
        Our custom loader that just modifies the loading of the base model so that patching and other stuff are supported.
        """
        if kwargs is not None:
            wrapped_model_kwargs, from_pretrained_kwargs = cls._split_kwargs(kwargs)
        else:
            from_pretrained_kwargs = {}
            wrapped_model_kwargs = {}

        base_model = get_model(config, tokenizer)

        model = cls(base_model)

        pretrained_model_name_or_path = config.model_name

        if isinstance(pretrained_model_name_or_path, str):
            filename = os.path.join(pretrained_model_name_or_path, "pytorch_model.bin")
            sharded_index_filename = os.path.join(pretrained_model_name_or_path, "pytorch_model.bin.index.json")
            is_sharded = False

            if not os.path.exists(filename):
                try:
                    filename = hf_hub_download(pretrained_model_name_or_path, "pytorch_model.bin", revision=revision)
                # Sharded
                except Exception:
                    if os.path.exists(sharded_index_filename):
                        index_file_name = sharded_index_filename
                    else:
                        index_file_name = hf_hub_download(
                            pretrained_model_name_or_path,
                            "pytorch_model.bin.index.json",
                            revision=revision,
                        )
                    with open(index_file_name, "r") as f:
                        index = json.load(f)
                    # Collect files containing weights from supported modules
                    files_to_download = set()
                    for k, v in index["weight_map"].items():
                        if any([module in k for module in cls._supported_modules]):
                            files_to_download.add(v)
                    is_sharded = True

            if is_sharded:
                # Merge each shard into a state dict
                # TODO: Optimize this to avoid wasting RAM
                state_dict = {}
                for shard_file in files_to_download:
                    filename = os.path.join(pretrained_model_name_or_path, shard_file)
                    # Download if shard file doesn't exist locally
                    if not os.path.exists(filename):
                        filename = hf_hub_download(pretrained_model_name_or_path, shard_file, revision=revision)
                    state_dict.update(torch.load(filename, map_location="cpu"))
            else:
                state_dict = torch.load(filename, map_location="cpu")
        else:
            state_dict = pretrained_model_name_or_path.state_dict()

        model.post_init(state_dict=state_dict)
        return model


@register_trainer
class CustomPPOTrainer(AcceleratePPOTrainer):
    def __init__(self, config, *args, **kwargs):
        # hm...
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.tokenizer.tokenizer_path, padding_side=config.tokenizer.padding_side
        ) # Loading our model requires the tokenizer to be loaded first
        
        super().__init__(*args, config=config, **kwargs)
        
        # Do not override pad_token with eos_token..
        self.tokenizer = AutoTokenizer.from_pretrained(config.tokenizer.tokenizer_path)
        self.tokenizer.padding_side = config.tokenizer.padding_side
        self.tokenizer.truncation_side = config.tokenizer.truncation_side
        

    def decode(
        self,
        prompts: List[torch.LongTensor],
        samples: List[torch.LongTensor],
        prompt_sizes: torch.LongTensor = None,
        append_eos_token: bool = True,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Decode tensor generations into lists of strings (`samples`: List[str], `prompts`: List[str], `outputs`: List[str])
        """
        assert append_eos_token is True
        
        if prompt_sizes is None:
            # Assuming prompts were left-padded
            prompt_sizes = [prompts.shape[1]] * len(prompts)

        str_samples, str_prompts, str_outputs = [], [], []

        for prompt, sample, prompt_size in zip(prompts, samples, prompt_sizes):
            if self.config.model.model_arch_type == "seq2seq":
                raise NotImplementedError("Decoding for seq2seq models is not implemented yet")
                output_start_ix = 0
            else:
                output_start_ix = prompt_size

            # Skip the padding token but not the other special tokens
            PAD_TOKEN_ID = self.tokenizer.pad_token_id

            str_prompt = self.tokenizer.decode(
                prompt[:prompt_size][prompt[:prompt_size] != PAD_TOKEN_ID], skip_special_tokens=False
            )
            str_output = self.tokenizer.decode(
                sample[output_start_ix:][sample[output_start_ix:] != PAD_TOKEN_ID], skip_special_tokens=False
            )

            trimmed = False
            # Trim outputs up to `self.stop_sequences` if any are present
            if self.stop_sequences:
                for stop in self.stop_sequences:
                    stop_ix = str_output.find(stop)
                    if stop_ix >= 0:
                        str_output = str_output[:stop_ix].rstrip()
                        trimmed = True

            # Recover the last <eos> if it was present in the original sample
            # or add one if it was trimmed with `self.stop_sequences`.
            # Only in cases when a generation ended due to `max_new_tokens` exhaustion,
            # <eos> token would not be present in the original sample
            if append_eos_token and (trimmed or sample[-1] == self.tokenizer.eos_token_id):
                str_output += self.tokenizer.eos_token

            str_prompts.append(str_prompt)
            str_outputs.append(str_output)

            if self.config.model.model_arch_type == "seq2seq":
                sample = str_prompt + self.tokenizer.sep_token + str_output
            else:
                sample = str_prompt + str_output + self.tokenizer.eos_token

            str_samples.append(sample)

        return str_samples, str_prompts, str_outputs

    def get_arch(self, config):
        if config.model.model_arch_type == "seq2seq":
            raise NotImplementedError("Seq2Seq models are not implemented yet")
            # model = Seq2SeqLMHydraWithValueHead(config.model.model_path, config.model.num_layers_unfrozen)
        else:
            model = CustomCausalLMHydraWithValueHead.from_pretrained(config.sft_config, self.tokenizer)

        return model

    def generate(self, input_ids, *args, **kwargs):
        preds = super().generate(input_ids, *args, **kwargs)

        # make sure the last token is the EOS token
        preds[:, -1] = self.tokenizer.eos_token_id

        return preds

    def generate_eval(self, input_ids, *args, **kwargs):
        preds = super().generate(input_ids, *args, **kwargs)

        preds[:, -1] = self.tokenizer.eos_token_id

        return preds


@register_datapipeline
class CustomPromptPipeline(BasePipeline):
    """
    Tokenizes prompts, unless they are already tokenized, and truncates them to `max_prompt_length` from the right
    """

    def __init__(self, prompts: List[str], max_prompt_length: int, tokenizer: PreTrainedTokenizer):
        super().__init__()

        model_inputs = tokenizer(
            prompts,
            truncation=True,
            padding=False,
            max_length=max_prompt_length,
            add_special_tokens=False,
        )

        prompts_tokens_ = model_inputs["input_ids"]
        attention_mask = model_inputs["attention_mask"]

        prompts_tokens = []

        assistant_token_id = tokenizer.convert_tokens_to_ids(QA_SPECIAL_TOKENS["Answer"])
        eos_token_id = tokenizer.eos_token_id

        # Due to truncation, special tokens may not be present ... so we add them (context is still incomplete)
        # not need to update attention_mask since it iw always 1
        for prompt_tokens in prompts_tokens_:
            prompts_tokens.append(prompt_tokens[:-2] + [eos_token_id, assistant_token_id])

        self.tokenizer = tokenizer
        self.prompts = [
            {"input_ids": tokens, "attention_mask": mask} for tokens, mask in zip(prompts_tokens, attention_mask)
        ]

    def __getitem__(self, ix: int):
        return self.prompts[ix]

    def __len__(self) -> int:
        return len(self.prompts)

    def create_loader(self, batch_size: int, shuffle=False) -> DataLoader:
        collate_fn = DataCollatorWithPadding(self.tokenizer) if self.tokenizer else torch.vstack
        return DataLoader(self, batch_size=batch_size, collate_fn=collate_fn, shuffle=shuffle)
