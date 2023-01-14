from argparse import Namespace

from utils import get_tokenizer


def test_tokenizer():
    get_tokenizer(Namespace(model_name="Salesforce/codegen-2B-multi", cache_dir=".cache"))
    get_tokenizer(Namespace(model_name="facebook/galactica-1.3b", cache_dir=".cache"))
    get_tokenizer(Namespace(model_name="", cache_dir=".cache"))
