from datasets import load_dataset

from .is_question import is_question
from .reddit import init_praw_reddit, scrap_subreddit

__all__ = ["is_question", "scrap_subreddit", "init_praw_reddit"]


def save_to_huggingface(df, name):
    TMP_FILE = "/tmp/save_to_huggingface_tmp.json"
    df.to_json(TMP_FILE, orient="records")
    hf_dataset = load_dataset("json", data_files=TMP_FILE)
    hf_dataset.push_to_hub(name)
