from dataclasses import dataclass

import datasets


@dataclass
class OpenAssistantConfig(datasets.BuilderConfig):
    """BuilderConfig for OpenAssistant datasets."""

    name: str = None
    version: datasets.Version = None
    description: str = None
    schema: str = None
    subset_id: str = None


lm_features = datasets.Features(
    {
        "text": datasets.Value("string"),
        "meta": [datasets.Value("string")],
    }
)
