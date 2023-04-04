from model_training.custom_datasets.rank_datasets import AnthropicRLHF, HellaSwagDataset, HFDataset, SHPDataset
from torch.utils.data import Dataset


def load_anthropic_rlhf() -> tuple[Dataset, Dataset]:
    train = AnthropicRLHF(split="train")
    validation = AnthropicRLHF(split="test")
    print(f"AnthropicRLHF dataset size: {len(train)}, {len(validation)}")
    return train, validation


def load_open_ai_summarize_from_feedback() -> tuple[Dataset, Dataset]:
    axis_test = HFDataset(split="test", subset="axis")
    axis_validation = HFDataset(split="validation", subset="axis")

    comp_train = HFDataset(split="train", subset="comparisons")
    comp_validation = HFDataset(split="validation", subset="comparisons")

    train = comp_train + axis_test
    validation = comp_validation + axis_validation

    print(f"HFDataset dataset size: {len(train)}, {len(validation)}")

    return train, validation


def load_shp() -> tuple[Dataset, Dataset]:
    train = SHPDataset(split="train")
    validation = SHPDataset(split="validation")
    return train, validation


def load_hellaswag() -> tuple[Dataset, Dataset]:
    train = HellaSwagDataset(split="train")
    validation = HellaSwagDataset(split="validation")
    return train, validation
