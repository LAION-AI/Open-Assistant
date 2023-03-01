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
This dataset is a set of instruction-response pairs from the HowTo100M dataset.
In each pair, the short instruction plays the role of Prompt,
and a long sequence of response plays the role of Response.
"""

import json
from typing import Dict, List, Tuple

import datasets

from .hub import OpenAssistantConfig, instruction_features

_CITATION = """\
@inproceedings{miech19howto100m,
   title={How{T}o100{M}: {L}earning a {T}ext-{V}ideo {E}mbedding by {W}atching {H}undred {M}illion {N}arrated {V}ideo {C}lips},
   author={Miech, Antoine and Zhukov, Dimitri and Alayrac, Jean-Baptiste and Tapaswi, Makarand and Laptev, Ivan and Sivic, Josef},
   booktitle={ICCV},
   year={2019},
}
"""

_DATASETNAME = "youtube_subs_howto100M"
_DISPLAYNAME = "YouTube Subtitles of Instructions: HowTo100M"
_DESCRIPTION = "A set of instruction-response pairs extracted from HowTo100M dataset"
_HOMEPAGE = "https://www.di.ens.fr/willow/research/howto100m/"
_LICENSE = "apache 2.0"
_URLS = {
    _DATASETNAME: {
        "train": "./data/youtube_subs_howto100M_train.jsonl",
        "test": "./data/youtube_subs_howto100M_test.jsonl",
        "validation": "./data/youtube_subs_howto100M_validation.jsonl",
    }
}
_SUPPORTED_TASKS = ["dialogue-modeling"]
_VERSION = "1.0.0"


class YouTubeSubsHowTo100MDataset(datasets.GeneratorBasedBuilder):
    """A set of instruction-response pairs extracted from HowTo100M dataset."""

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
            features=instruction_features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager) -> List[datasets.SplitGenerator]:
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


# This allows you to run your dataloader with `python [dataset_name].py` during development
# TODO: Remove this before making your PR
if __name__ == "__main__":
    datasets.load_dataset(__file__)
