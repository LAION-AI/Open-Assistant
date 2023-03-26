import json
import os

import numpy as np


def load_sampling_data(path):
    """
    Load sampling data and ensure appropriate keys are present.
    """

    if os.path.exists(path):
        data = json.load(open(path))
    else:
        raise FileNotFoundError(f"Sampling data {path} not found")

    if "prompts" not in data.keys():
        raise KeyError("sampling data should contain prompts key")

    keys = set(data["prompts"][0].keys())
    required_keys = set(["prompt", "results"])
    keys = keys.intersection(required_keys)
    if keys != required_keys:
        raise KeyError(f"Missing keys {required_keys - keys} ")

    return data


def write_to_json(filename, data):
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def describe_samples(samples):
    reward_scores = []
    for item in samples:
        reward_scores.extend([float(output[1]) for output in item["outputs"]])

    return {
        "mean": np.mean(reward_scores).astype(str),
        "min": np.min(reward_scores).astype(str),
        "max": np.max(reward_scores).astype(str),
    }
