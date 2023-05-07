import pytest
from langcodes import Language
from model_training.custom_datasets.entities import Mode
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS, DatasetEntry


def test_dataset_entry_rm_mode():
    ds_entry = DatasetEntry(
        questions=["Instruction A."],
        answers=[["Highest Scored Answer to A.", "Second Highest Scored Answer to A"]],
    )

    eos = "<|endofline|>"
    formatted_rm = ds_entry.get_formatted(mode=Mode.rm, eos_token=eos)
    expected_rm = (
        ["<|prompter|>Instruction A.<|endofline|>"],
        [
            "<|assistant|>Highest Scored Answer to A.<|endofline|>",
            "<|assistant|>Second Highest Scored Answer to A<|endofline|>",
        ],
    )
    assert formatted_rm == expected_rm


def test_dataset_entry_sft_mode_compatible_with_rm():
    ds_entry = DatasetEntry(
        questions=["Instruction A.", "Followup Instruction B."],
        answers=[
            ["Highest Scored Answer to A.", "Second Highest Scored Answer to A"],
            ["Highest Scored Answer to B.", "Second Highest Scored Answer to B"],
        ],
    )
    eos = "<|endofline|>"
    formatted_sft = ds_entry.get_formatted(mode=Mode.sft, eos_token=eos)
    expected_sft = [
        f"{QA_SPECIAL_TOKENS['Question']}{ds_entry.questions[0]}{eos}",
        f"{QA_SPECIAL_TOKENS['Answer']}{ds_entry.answers[0][0]}{eos}",
        f"{QA_SPECIAL_TOKENS['Question']}{ds_entry.questions[1]}{eos}",
        f"{QA_SPECIAL_TOKENS['Answer']}{ds_entry.answers[1][0]}{eos}",
    ]
    assert formatted_sft == expected_sft


def test_dataset_entry_formatting_missing_lang():
    ds_entry = DatasetEntry(
        questions=["What is the capital of France?"],
        answers=["The capital of France is Paris."],
        context="Some context",
        length=100,
        quality=1.0,
        humor=0.0,
        creativity=0.0,
    )
    formatted = ds_entry.get_formatted(Mode.sft, "<|endofline|>")
    assert len(formatted) == 3
    assert "length: 100" in formatted[0]
    assert "quality: 1.0" in formatted[0]
    assert "humor: 0.0" in formatted[0]
    assert "creativity: 0.0" in formatted[0]
    assert "Some context" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Question']}What is the capital of France?<|endofline|>" == formatted[1]
    assert f"{QA_SPECIAL_TOKENS['Answer']}The capital of France is Paris.<|endofline|>" == formatted[2]


def test_dataset_entry():
    ds_entry = DatasetEntry(
        questions=["What is the capital of France?"],
        answers=["The capital of France is Paris."],
        context="Some context",
        lang="en",
        length=100,
        quality=1.0,
        humor=0.0,
        creativity=0.0,
    )
    formatted = ds_entry.get_formatted(Mode.sft, "<|endofline|>")
    assert len(formatted) == 3
    assert "lang: en" in formatted[0]
    assert "length: 100" in formatted[0]
    assert "quality: 1.0" in formatted[0]
    assert "humor: 0.0" in formatted[0]
    assert "creativity: 0.0" in formatted[0]
    assert "Some context" in formatted[0]
    assert f"{QA_SPECIAL_TOKENS['Question']}What is the capital of France?<|endofline|>" == formatted[1]
    assert f"{QA_SPECIAL_TOKENS['Answer']}The capital of France is Paris.<|endofline|>" == formatted[2]


def test_dataset_entry_float_violations():
    fields = {
        "questions": ["What is the capital of France?"],
        "answers": ["The capital of France is Paris."],
        "context": "Some context",
        "lang": Language("en"),
        "length": 100,
    }
    with pytest.raises(ValueError, match="Field quality must be between 0 and 1. Received -1.0"):
        DatasetEntry(**fields, quality=-1.0, humor=0.0, creativity=0.0)

    with pytest.raises(ValueError, match="Field humor must be between 0 and 1. Received 2"):
        DatasetEntry(**fields, quality=1.0, humor=2.0, creativity=0.0)

    with pytest.raises(ValueError, match="Field creativity must be between 0 and 1. Received 1000.0"):
        DatasetEntry(**fields, quality=1.0, humor=2.0, creativity=1000.0)


def test_dataset_entry_int_violations():
    fields = {
        "questions": ["What is the capital of France?"],
        "answers": ["The capital of France is Paris."],
        "context": "Some context",
        "lang": Language("en"),
        "quality": -1.0,
        "humor": 0.0,
        "creativity": 0.0,
    }
    with pytest.raises(ValueError, match="Length cannot be lower than 0. Received -1"):
        DatasetEntry(**fields, length=-1)
