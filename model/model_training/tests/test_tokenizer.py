from models.tokenization_llama import LLaMATokenizer
from transformers import AutoTokenizer


def testing_llama_tokenizer():
    texts = [
        "danke schön",
        "This is fined",
        "Je vous remercie. C'est très gentil de votre part.",
        "Hi\nWho are you?",
        '```Python\nname = input("What is your name? ")\nprint("Hello, " + name + "! Nice to meet you!")\n```',
    ]
    tokenizer = LLaMATokenizer.from_pretrained("decapoda-research/llama-7b-hf")
    # modified from deberta fast tokenizers
    new_tokenizer_cand1 = AutoTokenizer.from_pretrained(
        "theblackcat102/llama-7b-test", download_mode="force_redownload"
    )
    # modified from t5 tokenizers
    new_tokenizer_cand2 = AutoTokenizer.from_pretrained(
        "theblackcat102/llama-fast-tokenizer", download_mode="force_redownload"
    )

    for text in texts:
        ref_tokens = tokenizer(text)["input_ids"]
        cand1_tokens = new_tokenizer_cand1(text, add_special_tokens=False)["input_ids"]
        cand2_tokens = new_tokenizer_cand2(text, add_special_tokens=False)["input_ids"]
        if cand1_tokens != ref_tokens:
            print("reference : ", ref_tokens)
            print("deberta tokens", cand1_tokens)
            print("reference decode text:\n{}\n-------\n".format(tokenizer.decode(ref_tokens)))
            # basically we can test if the converted tokens are working
            # by using the reference tokenizer for decoding
            print("deberta decode text:\n{}\n-------\n".format(tokenizer.decode(cand1_tokens)))
        else:
            pass
        if cand2_tokens != ref_tokens:
            print("reference : ", ref_tokens)
            print("t5 tokens", cand2_tokens)
            print("reference decode text:\n{}\n-------\n".format(tokenizer.decode(ref_tokens)))
            # basically we can test if the converted tokens are working
            # by using the reference tokenizer for decoding
            print("t5 decode text:\n{}\n-------\n".format(tokenizer.decode(cand2_tokens)))


if __name__ == "__main__":
    testing_llama_tokenizer()
