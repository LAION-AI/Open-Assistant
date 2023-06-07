import pytest
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS, DatasetEntrySft, Role, Utterance


def test_dataset_entry_formatting_missing_lang():
    ds_entry = DatasetEntrySft(
        conversation=[
            Utterance(
                text="What is the capital of France?",
                role=Role.prompter,
            ),
            Utterance(
                text="The capital of France is Paris.",
                role=Role.assistant,
                context="Some context",
                quality=1.0,
                humor=0.0,
                creativity=0.0,
            ),
        ],
    )
    formatted = ds_entry.get_formatted(
        "<|endofline|>",
        use_system_tag=True,
        system_property_dropout=0.0,
        system_add_length=True,
    )
    assert len(formatted) == 2
    # this is just optional
    assert "length: 2" in formatted[0]
    assert "quality: 1.0" in formatted[0]
    assert "humor: 0.0" in formatted[0]
    assert "creativity: 0.0" in formatted[0]
    assert "Some context" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Question']}What is the capital of France?<|endofline|>" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Answer']}The capital of France is Paris.<|endofline|>" == formatted[1]


def test_dataset_entry():
    ds_entry = DatasetEntrySft(
        conversation=[
            Utterance(
                text="What is the capital of France?",
                role=Role.prompter,
            ),
            Utterance(
                text="The capital of France is Paris.",
                role=Role.assistant,
                context="Some context",
                lang="en",
                quality=1.0,
                humor=0.0,
                creativity=0.0,
            ),
        ],
    )
    formatted = ds_entry.get_formatted(
        "<|endofline|>",
        use_system_tag=True,
        system_property_dropout=0.0,
        system_add_length=True,
    )
    assert len(formatted) == 2
    assert "lang: en" in formatted[0]
    assert "length: 2" in formatted[0]
    assert "quality: 1.0" in formatted[0]
    assert "humor: 0.0" in formatted[0]
    assert "creativity: 0.0" in formatted[0]
    assert "Some context" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Question']}What is the capital of France?<|endofline|>" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Answer']}The capital of France is Paris.<|endofline|>" == formatted[1]


def test_dataset_entry_float_violations():
    fields = {
        "content": "The capital of France is Paris.",
        "context": "Some context",
        "lang": "en",
    }
    with pytest.raises(ValueError, match="Field quality must be between 0 and 1. Received: -1.0"):
        Utterance(**fields, quality=-1.0, humor=0.0, creativity=0.0)

    with pytest.raises(ValueError, match="Field humor must be between 0 and 1. Received: 2"):
        Utterance(**fields, quality=1.0, humor=2.0, creativity=0.0)

    with pytest.raises(ValueError, match="Field creativity must be between 0 and 1. Received: 1000.0"):
        Utterance(**fields, quality=1.0, humor=2.0, creativity=1000.0)
