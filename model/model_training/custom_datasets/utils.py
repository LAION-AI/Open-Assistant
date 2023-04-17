FILTER_BY_WORDS = ["openai"]


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
        if word in text.lower():
            return None
    return text
