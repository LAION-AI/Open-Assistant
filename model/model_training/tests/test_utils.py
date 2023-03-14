from argparse import Namespace

import pytest
from utils import TOKENIZER_CONFIGS, get_tokenizer, match_tokenizer_name


def test_tokenizer():
    get_tokenizer(Namespace(model_name="Salesforce/codegen-2B-multi", cache_dir=".cache"))
    get_tokenizer(Namespace(model_name="facebook/galactica-1.3b", cache_dir=".cache"))


def test_tokenizer_successful_match():
    for config_name, config in TOKENIZER_CONFIGS.items():
        found_config = match_tokenizer_name(config_name)
        assert found_config == config


def test_tokenizer_partial_match():
    for config_name in ["facebook/galactica-1.3b", "togethercomputer/GPT-JT-6B-v1", "Salesforce/codegen-2B-multi"]:
        found_config = match_tokenizer_name(config_name)
        assert found_config


def test_tokenizer_failed_match():
    for fake_config_name in ["not-a-model", "fake"]:
        with pytest.raises(ValueError):
            match_tokenizer_name(fake_config_name)
