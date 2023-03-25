import json

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
