from model_training.custom_datasets.rank_datasets import AnthropicRLHF, HFDataset


def load_anthropic_rlhf():
    train = AnthropicRLHF(split="train")
    validation = AnthropicRLHF(split="test")

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
