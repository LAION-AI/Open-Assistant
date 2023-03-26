from collections import defaultdict

import torch
from model_training.custom_datasets.ranking_collator import RankingDataCollator
from torch.utils.data import DataLoader, Dataset


def get_sampling_dataloader(data, tokenizer, max_length, batch_size):
    collate_fn = SamplingDataCollator(tokenizer, max_length=max_length)
    dataset = SamplingDataset(data)
    return DataLoader(dataset, collate_fn=collate_fn, batch_size=batch_size)


class SamplingDataCollator(RankingDataCollator):
    def __call__(self, examples):
        flat_tokenized = []
        sampling_ids = []
        for example in examples:
            prefix, reply, sampling = example
            sampling_ids.append(sampling)
            tokenized = self.process_one((prefix, reply))
            flat_tokenized.extend(tokenized)

        batch = self.tokenizer.pad(
            flat_tokenized,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )

        if "token_type_ids" in batch:
            batch.pop("token_type_ids")

        batch["sampling"] = torch.tensor(sampling_ids)
        return batch


class SamplingDataset(Dataset):

    """
    Dataset for loading sampling reports
    """

    def __init__(self, dataset):
        super().__init__()

        self.dataset = []
        sampling_list = []
        for data in dataset["prompts"]:
            prompt = data["prompt"]
            for result in data["results"]:
                sampling = result["sampling_config"]
                for output in result["outputs"]:
                    self.dataset.append((prompt, output, sampling))
                if sampling not in sampling_list:
                    sampling_list.append(sampling)

        self.label2id = self.get_label2id(sampling_list)

    def get_label2id(self, sampling_list):
        return {v: k for k, v in enumerate(sampling_list)}

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        prefix, reply, sampling = self.dataset[idx]
        sampling = self.label2id[sampling]

        return ([prefix], [reply], sampling)


class RejectionSamplingDataset(Dataset):
    def __init__(self, dataset):
        self.prompt_answer = defaultdict(list)
        for data in dataset["prompts"]:
            prompt = data["prompt"].strip()
            if prompt not in self.prompt_answer.keys():
                self.prompt_answer[prompt] = []

            outputs = [output for result in data["results"] for output in result["outputs"]]
            self.prompt_answer[prompt].extend(outputs)

        self.prompts = list(self.prompt_answer.keys())

    def __len__(self):
        return len(self.prompts)

    def __getitem__(self, index):
        prompt = self.prompts[index]
        replies = self.prompt_answer.get(prompt)

        return prompt, replies, index
