from model_training.custom_datasets.formatting import format_pairs, format_reply
from torch.utils.data import DataLoader, Dataset


def get_sampling_dataloader(data, tokenizer, max_len, batch_size, device):
    dataset = SamplingDataset(data, tokenizer, max_len, device)
    return DataLoader(dataset, batch_size=batch_size)


class SamplingDataset(Dataset):

    """
    Dataset for loading sampling reports
    """

    def __init__(self, dataset, tokenizer, max_len, device):
        super().__init__()

        self.device = device
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.dataset = []
        sampling_list = []
        for data in dataset["prompts"][:4]:
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
        prefix = format_pairs([prefix], self.tokenizer.eos_token)[0]
        reply = format_reply(reply, self.tokenizer.eos_token)[0]
        encodings = self.tokenizer(
            prefix,
            reply,
            add_special_tokens=True,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        encodings["sampling"] = self.label2id[sampling]

        return encodings
