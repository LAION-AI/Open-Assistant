from collections import defaultdict

import numpy as np
from datasets import load_dataset
from torch.utils.data import Dataset

SEED = 2020


class SHPDataset(Dataset):
    """
    Dataset class to load stanfordnlp/SHP for Reward Modeling
    """

    name = "SHP"

    def __init__(self, split):
        super().__init__()

        self.post_dict = defaultdict(dict)
        self.postids = []
        dataset = load_dataset("stanfordnlp/SHP", split=split)
        for item in dataset:
            postid = item.get("post_id")
            self.postids.append(postid)
            score_A, score_B = [item.get(key) for key in ("score_A", "score_B")]
            answers = [item.get(key) for key in ("human_ref_A", "human_ref_B")]
            if score_B > score_A:
                answers = list(reversed(answers))

            self.post_dict[postid].update({"post": item.get("history"), "answers": answers})

    def __len__(self):
        return len(self.postids)

    def __getitem__(self, idx):
        postid = self.postids[idx]
        post, answers = self.post_dict.get(postid, {}).values()
        return [post], answers


class HellaSwagDataset(Dataset):

    """
    Dataset class to use data from https://arxiv.org/pdf/1905.07830.pdf
    for Reward modeling
    """

    name = "hellaswag"

    def __init__(self, split) -> None:
        super().__init__()

        np.random.seed(SEED)
        self.dataset_list = []
        dataset = load_dataset("AlekseyKorshuk/hellaswag", split=split)
        for item in dataset:
            context = item.get("ctx")
            endings = item.get("endings")
            selected = endings.pop(item.get("label"))
            ordered_ends = [selected, np.random.choice(endings)]
            self.dataset_list.append({"context": context, "completions": ordered_ends})

    def __len__(self):
        return len(self.dataset_list)

    def __getitem__(self, idx):
        context, completions = self.dataset_list[idx].values()
        return [context], completions


class HFDataset(Dataset):

    """
    Dataset class to use data from openai/summarize_from_feedback for Reward modeling.
    Summaries ranked by overall score.
    """

    name = "hfsummary"

    def __init__(self, split=None) -> None:
        super().__init__()

        dataset = load_dataset("openai/summarize_from_feedback", "axis", split=split)
        self.post_ids = []
        self.post_dict = defaultdict(dict)
        for item in dataset:
            if item["summary"].get("axes").get("overall") is not None:
                post_id = item.get("info")["id"]
                if post_id not in self.post_ids:
                    self.post_ids.append(post_id)
                    item_content = item["info"]["post"] or item["info"]["article"]
                    self.post_dict[post_id].update({"post": item_content, "summaries": [item["summary"]]})
                else:
                    self.post_dict[post_id]["summaries"].append(item["summary"])

    def __len__(self):
        return len(self.post_ids)

    def __getitem__(self, idx):
        post, summaries = self.post_dict[self.post_ids[idx]].values()
        summaries = sorted(summaries, key=lambda x: x["axes"]["overall"], reverse=True)
        summaries = [summary["text"] for summary in summaries]
        return [post], summaries
