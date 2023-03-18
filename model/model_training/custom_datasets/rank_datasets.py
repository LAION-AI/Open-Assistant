from torch.utils.data import Dataset
from datasets import load_dataset
from collections import defaultdict


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
            score_A, score_B = [item.get(key) for key in ("score_A","score_B")]
            answers = [item.get(key) for key in ("human_ref_A","human_ref_B")]
            if score_B > score_A:
                answers = list(reversed(answers))

            self.post_dict[postid].update({"post": item.get("history"), "answers":answers})

    def __len__(self):
        return len(self.postids)


    def __getitem__(self, idx):

        postid = self.postids[idx]
        post, answers = self.post_dict.get(postid,{}).values()
        return post, answers

