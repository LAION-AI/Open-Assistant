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

    def __init__(self, split=None, subset="axis") -> None:
        super().__init__()
        # axis subset contains splits 'test' and 'validation'
        # comparisons subset contains splits 'train' and 'validation'
        dataset = load_dataset("openai/summarize_from_feedback", subset, split=split)
        self.subset = subset

        # in axis subset the summaries are ranked
        self.axis_post_ids = []
        self.axis_post_dict = defaultdict(dict)

        # in comparison subset we have each time a pair
        # of summarizations and then the chosen out of 2
        self.comparisons = []

        if subset == "axis":
            self._handle_axis(dataset)
        else:
            self._handle_comparisons(dataset)

    def _handle_comparisons(self, dataset):
        for item in dataset:
            choice = item["choice"]  # indicates the preferred summary
            full_post = item["info"]["post"]
            summaries = [item["summaries"][choice]["text"], item["summaries"][1 - choice]["text"]]
            self.comparisons.append([[full_post], summaries])

    def _handle_axis(self, dataset):
        for item in dataset:
            if item["summary"].get("axes").get("overall") is not None:
                post_id = item.get("info")["id"]
                if post_id not in self.axis_post_ids:
                    self.axis_post_ids.append(post_id)
                    item_content = item["info"]["post"] or item["info"]["article"]
                    self.axis_post_dict[post_id].update({"post": item_content, "summaries": [item["summary"]]})
                else:
                    self.axis_post_dict[post_id]["summaries"].append(item["summary"])

    def __len__(self):
        if self.subset == "axis":
            return len(self.axis_post_ids)
        return len(self.comparisons)

    def __getitem__(self, idx):
        if self.subset == "axis":
            post, summaries = self.axis_post_dict[self.axis_post_ids[idx]].values()
            summaries = sorted(summaries, key=lambda x: x["axes"]["overall"], reverse=True)
            summaries = [summary["text"] for summary in summaries]
            return [post], summaries
        return self.comparisons[idx]
