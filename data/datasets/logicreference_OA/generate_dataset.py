# Copyright 2023 The Google Research Authors.
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

"""Driver file that generates IID/OOD/length splits.
"""


import os
import random

import rules
import splits
import tensorflow as tf
from absl import app

# Generation parameters:
# TARGET_FOLDER = "/path/to/generate/dataset/"
TARGET_FOLDER = "./e_txt/"
ANSWER_AT_THE_END = True
LENGTH_DISTRIBUTION = [0.425, 0.3, 0.2, 0.05, 0.025]
N_INFERENCE_PROBLEMS = 10000
N_VARIATIONS = 25
N_EXAMPLES = 55000
TRAIN_RATIO = 1
LENGTH_SPLIT_THRESHOLD = 4
RANDOM_SEED = 1111


def create_string_feature(values):
    """Creates TensorFlow string features.

    Args:
      values: A sequence of unicode strings.

    Returns:
      An entry of int tf.train.Feature.
    """
    # Converts to `str` (in Python 2) and `bytes` (in Python 3) as
    # `tf.train.Feature` only takes bytes.
    values = [value.encode("utf-8") for value in values]

    feature = tf.train.Feature(bytes_list=tf.train.BytesList(value=values))
    return feature


def generate_t5_split(path, file_name, examples):
    print(f"Generating split of size {len(examples)} at {path}")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, file_name), "w") as f:
        for example in examples:
            f.write(f"INSTRUCTION: {example.inputs}\n")
            f.write(f"RESPONSE: {example.targets}\n")
            f.write("SOURCE: LogicInference Dataset e\n\n")


def main(_):
    rules.precompute_rules()

    suffix = ""
    if ANSWER_AT_THE_END:
        suffix = "_e"
    folder_iid_name = "logic_inference_iid" + suffix

    # Generate each of the splits:
    print("IID:")
    random.seed(RANDOM_SEED)
    (train_examples, test_examples) = splits.generate_training_and_test_sets_iid(
        N_INFERENCE_PROBLEMS,
        N_VARIATIONS,
        N_EXAMPLES,
        TRAIN_RATIO,
        length_distribution=LENGTH_DISTRIBUTION,
        answer_at_the_end=ANSWER_AT_THE_END,
    )
    generate_t5_split(
        os.path.join(TARGET_FOLDER, folder_iid_name),
        f"{folder_iid_name}-train_tf_examples-00000-of-00001",
        train_examples,
    )
    generate_t5_split(
        os.path.join(TARGET_FOLDER, folder_iid_name),
        f"{folder_iid_name}-test_tf_examples-00000-of-00001",
        test_examples,
    )

    # print("OOD:")
    # random.seed(RANDOM_SEED)
    # (train_examples, test_examples) = splits.generate_training_and_test_sets_ood(
    #     N_INFERENCE_PROBLEMS, N_VARIATIONS, N_EXAMPLES, TRAIN_RATIO,
    #     length_distribution=LENGTH_DISTRIBUTION,
    #     answer_at_the_end=ANSWER_AT_THE_END)
    # generate_t5_split(os.path.join(TARGET_FOLDER, folder_ood_name),
    #                   f"{folder_ood_name}-train_tf_examples-00000-of-00001",
    #                   train_examples)
    # generate_t5_split(os.path.join(TARGET_FOLDER, folder_ood_name),
    #                   f"{folder_ood_name}-test_tf_examples-00000-of-00001",
    #                   test_examples)
    #
    # print("Length:")
    # random.seed(RANDOM_SEED)
    # (train_examples,
    #  test_examples) = splits.generate_training_and_test_sets_length(
    #      N_INFERENCE_PROBLEMS,
    #      N_VARIATIONS,
    #      N_EXAMPLES,
    #      LENGTH_SPLIT_THRESHOLD,
    #      length_distribution=LENGTH_DISTRIBUTION,
    #      answer_at_the_end=ANSWER_AT_THE_END)
    # generate_t5_split(
    #     os.path.join(TARGET_FOLDER, folder_length_name),
    #     f"{folder_length_name}-train_tf_examples-00000-of-00001", train_examples)
    # generate_t5_split(
    #     os.path.join(TARGET_FOLDER, folder_length_name),
    #     f"{folder_length_name}-test_tf_examples-00000-of-00001", test_examples)


if __name__ == "__main__":
    app.run(main)
