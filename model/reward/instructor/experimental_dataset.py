"""
    HFSummary

        I want to train a multi regression model on axis_evals dataset mainly we can estimate the score of these score

         - {"overall": "6", "accuracy": "6", "coverage": "6", "coherence": "7"}

        Should be better than just a preference score

"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import torch
from datasets import load_dataset
from torch.utils.data import Dataset
from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase


@dataclass
class DataCollatorForSummaryScore:
    """

    Data collator that will dynamically pad the inputs for multiple choice received.

    """

    tokenizer: PreTrainedTokenizerBase
    num_choices: int = 2
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    drop_token_type: bool = False  # galactica

    def __call__(self, batch):
        features = []
        labels = []
        for feature, label in batch:
            features.append(feature)
            labels.append(label)

        batch_feature = self.tokenizer.pad(
            features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        if self.drop_token_type:
            batch_feature.pop("token_type_ids")
        # batch = {k: v.view(batch_size, self.num_choices, -1) for k, v in batch.items()}
        batch_feature["labels"] = torch.from_numpy(np.array(labels)).float()
        return batch_feature


class HFSummaryQuality(Dataset):
    def __init__(self, split, tokenizer, max_length=300) -> None:
        super().__init__()
        assert split in ("validation", "test")
        dataset = load_dataset("openai/summarize_from_feedback", "axis")[split]
        self.max_length = max_length
        mean_scores = defaultdict(list)
        self.contexts = []
        self.responses = []
        self.labels = []
        for data in dataset:
            if "article" in data["info"] and data["info"]["article"] is not None:
                context = data["info"]["article"]
            elif "post" in data["info"]:
                context = data["info"]["post"]
            self.contexts.append(context)

            response = data["summary"]["text"]
            self.responses.append(response)
            self.labels.append(data["summary"]["axes"])
            for axis, score in data["summary"]["axes"].items():
                if score is not None:
                    mean_scores[axis].append(score)

        self.label2idx = {key: idx for idx, key in enumerate(mean_scores.keys())}
        self.label2mean = {key: np.mean(scores) for key, scores in mean_scores.items()}
        self.tokenizer = tokenizer
        print(self.label2idx)

    def __len__(self):
        return len(self.responses)

    def __getitem__(self, index):
        context = self.contexts[index]
        # return pairs of comparison
        response = self.responses[index]
        labels = np.zeros(len(self.label2idx))
        for key, score in self.labels[index].items():
            labels[self.label2idx[key]] = (self.label2mean[key] if score is None else score) / 10
        return self.tokenizer(context, response, truncation=True, max_length=self.max_length), labels
