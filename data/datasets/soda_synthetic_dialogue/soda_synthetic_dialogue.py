# Copyright 2023 The OpenAssistant Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This dataset is a set of dialogues synthesized from the SODA dataset.
In each dialogue, User and Assistant have a conversation about a story.

The original collab notebook for this dataset can be found at:
https://colab.research.google.com/drive/1Sw3px5dP8whdqT7QMNoqwmqIasZkMbJi?usp=sharing
"""

import json
from typing import Dict, List, Tuple

import datasets

from .hub import OpenAssistantConfig, features

_CITATION = """\
@article{ontocord2023sodasynth,
  author    = {ontocord and Jeffrey Quesnelle},
  title     = {SODA Synthetic Dialogue},
  year      = {2023}
}
"""
_DATASETNAME = "soda_synthetic_dialogue"
_DISPLAYNAME = "🥤SODA Synthetic Dialogue"
_DESCRIPTION = "A set of dialogues synthesized from the SODA dataset."
_HOMEPAGE = ""
_LICENSE = "mit"
_URLS = {
    _DATASETNAME: {"train": "./data/train.jsonl", "test": "./data/test.jsonl", "validation": "./data/validation.jsonl"}
}
_SUPPORTED_TASKS = ["dialogue-modeling"]
_VERSION = "1.0.0"


class SODASyntheticDialogueDataset(datasets.GeneratorBasedBuilder):
    """A set of dialogues synthesized from the SODA dataset."""

    VERSION = datasets.Version(_VERSION)

    BUILDER_CONFIGS = [
        OpenAssistantConfig(
            name=f"{_DATASETNAME}_dialogue_modeling",
            version=VERSION,
            description=f"OpenAssistant dataset config for {_DATASETNAME}",
            schema="dialogue_modeling",
            subset_id=_DATASETNAME,
        )
    ]

    DEFAULT_CONFIG_NAME = f"{_DATASETNAME}_dialogue_modeling"

    def _info(self) -> datasets.DatasetInfo:
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager) -> List[datasets.SplitGenerator]:
        """Returns SplitGenerators."""

        urls = _URLS[_DATASETNAME]
        data_dir = dl_manager.download_and_extract(urls)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": data_dir, "split": "train"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": data_dir, "split": "test"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"filepath": data_dir, "split": "validation"},
            ),
        ]

    def _generate_examples(self, filepath, split: str) -> Tuple[int, Dict]:
        """Yields examples as (key, example) tuples."""

        if self.config.schema == "dialogue_modeling":
            key = 0
            with open(filepath[split], "r", encoding="utf8") as data:
                while True:
                    line = data.readline()
                    if not line:
                        return
                    yield key, json.loads(line)
                    key += 1
