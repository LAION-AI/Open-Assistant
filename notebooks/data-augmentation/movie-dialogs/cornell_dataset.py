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


import json
from typing import Dict, List, Tuple

import datasets


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
This dataset is a set of dialogues synthesized from the Cornell Movie dialog Corpus.
"""

import json
from typing import Dict, List, Tuple

import datasets


from dataclasses import dataclass

@dataclass
class OpenAssistantConfig(datasets.BuilderConfig):
    """BuilderConfig for OpenAssistant datasets."""

    name: str = None
    version: datasets.Version = None
    description: str = None
    schema: str = None
    subset_id: str = None


features = datasets.Features(
    {
        "conversation": datasets.Value("string"),
    }
)



_CITATION = """
@InProceedings{Danescu-Niculescu-Mizil+Lee:11a,

  author={Cristian Danescu-Niculescu-Mizil and Lillian Lee},

  title={Chameleons in imagined conversations:

  A new approach to understanding coordination of linguistic style in dialogs.},

  booktitle={Proceedings of the

        Workshop on Cognitive Modeling and Computational Linguistics, ACL 2011},

  year={2011}

}
"""
_DATASETNAME = "cornell-movie-corpus"
_DISPLAYNAME = "Cornell Movie Corpus"
_DESCRIPTION = "A set of dialogues synthesized from the Cornell Movie Corpus."
_HOMEPAGE = ""
_LICENSE = "mit"
_URLS = {
    _DATASETNAME: {"train": "./train.jsonl"}
}
_SUPPORTED_TASKS = ["dialogue-modeling"]
_VERSION = "1.0.0"

class CornellDialogueDataset(datasets.GeneratorBasedBuilder):
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
            )
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
