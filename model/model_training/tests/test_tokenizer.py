from models.tokenization_llama import LLaMaConverter, LLaMATokenizer
from models.tokenization_llama_fast import LLaMATokenizerFast
from transformers import AutoTokenizer
from transformers.convert_slow_tokenizer import SLOW_TO_FAST_CONVERTERS

SLOW_TO_FAST_CONVERTERS["LLaMATokenizer"] = LLaMaConverter


def test_converter():
    # still byte fallback warning, not good
    converted_tokenizer = LLaMATokenizerFast.from_pretrained("decapoda-research/llama-7b-hf")
    # converted_tokenizer = LLaMaConverter(tokenizer).converted()
    encodes = converted_tokenizer.encode_plus("what it is", return_offsets_mapping=True)
    assert "offset_mapping" in encodes
    print(converted_tokenizer)


def test_llama_tokenizer():
    texts = [
        "danke schön",
        "This is fined",
        "你好啊",
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
    test_converter()
