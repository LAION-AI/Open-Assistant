# mostly taken from
# https://huggingface.co/datasets/gozfarb/ShareGPT_Vicuna_unfiltered/blob/main/optional_clean.py,
# https://huggingface.co/datasets/ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered/blob/main/wizardlm_clean.py
FILTER_BY_WORDS = [
    "as a language model",
    "as an AI language model",
    "As a large language model",
    "As an AI ",
    "an AI language model you don't have",
    "As an AI language model, I cannot",
    "As an AI language model, I do not",
    "As an AI language model, I am not able",
    "As an AI language model, I don't have personal",
    "I am an AI language model and do not",
    "As an AI language model, I don't have",
    "As an AI language model, I am only able",
    "AI language model and I do not",
    "As an AI language model, I cannot modify",
    "As an AI language model, I do not",
    "I know as an AI language model you don't have",
    "as an AI language model, you cannot",
    "I'm sorry, but as an AI language model",
    "As an AI language model, I don't have",
    "I'm an AI ",
    "I am an AI ",
    "As your dedicated AI language model",
    "As a hypothetical AI",
    "As a neutral AI",
    "my knowledge cutoff",
    "my knowledge cut off",
    "As a machine",
    "I cannot assist",
    "I do not have personal preferences",
    "I don't have personal preferences",
    "Unfortunately, I cannot provide",
    "I'm sorry, I cannot",
    "I'm sorry, I cannot generate",
    "AI cannot create or program",
    "I'm afraid I cannot create",
    "OpenAI",
]


def _filter_by_words(text: str, filter_words: list[str] | None = None) -> None | str:
    """Used to filter text that contains one of the `FILTER_BY_WORDS`. If so we return `None`
       otherwise we return the string

    Args:
        text (str): text to be filtered

    Returns:
        None | str: filtered text
    """
    filter_words = filter_words or FILTER_BY_WORDS
    for word in filter_words:
        if word.lower() in text.lower():
            return None
    return text
