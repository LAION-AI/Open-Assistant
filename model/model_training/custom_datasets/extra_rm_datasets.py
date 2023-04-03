from model_training.custom_datasets.rank_datasets import HFDataset
from reward.instructor.rank_datasets import AnthropicRLHF


def load_anthroopic_rlhf():
    train = AnthropicRLHF(split="train", mode="rm")
    validation = AnthropicRLHF(split="test", mode="rm")

    print(f"AnthropicRLHF extra dataset size: {len(train)}, {len(validation)}")

    return train, validation


def load_open_ai_summarize_from_feedback():
    axis_test = HFDataset(split="test", subset="axis")
    axis_validation = HFDataset(split="validation", subset="axis")

    comp_train = HFDataset(split="train", subset="comparisons")
    comp_validation = HFDataset(split="validation", subset="comparisons")

    train = comp_train + axis_test
    validation = comp_validation + axis_validation

    print(f"HFDataset extra dataset size: {len(train)}, {len(validation)}")

    return train, validation
