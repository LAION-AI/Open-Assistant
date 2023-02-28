---
annotations_creators:
  - no-annotation
language:
  - en
language_creators:
  - machine-generated
license:
  - mit
multilinguality:
  - monolingual
pretty_name: "SODA Synthetic Dialogue"
size_categories:
  - 1M<n<10M
source_datasets:
  - extended|allenai/soda
tags:
  - open-assistant
  - conversations-summarization
task_categories:
  - conversational
task_ids:
  - dialogue-generation
dataset_info:
  features:
    - name: conversation
      dtype: string
  config_name: soda_synthetic_dialogue_dialogue_modeling
  splits:
    - name: train
      num_bytes: 1524941476
      num_examples: 1191582
    - name: test
      num_bytes: 190565707
      num_examples: 148968
    - name: validation
      num_bytes: 187161878
      num_examples: 146346
  download_size: 1952926579
  dataset_size: 1902669061
---

# Dataset Card for 🥤SODA Synthetic Dialogue

## Dataset Description

- **Repository:**
  [Code](https://github.com/LAION-AI/Open-Assistant/data/datasets/soda_synthetic_dialogue/)

## Dataset Summary

🥤SODA Synthetic Dialogue is a set of synthetic dialogues between Assistant and
User. In each conversation, User asks Assistant to perform summarization or
story generation tasks based on a snippet of an existing dialogue, story, or
from a title or theme.

This data was created by synthesizing the dialogues in
[🥤Soda](https://huggingface.co/datasets/allenai/soda) and applying a set of
templates to generate the conversation. The original research paper can be found
[here](https://arxiv.org/pdf/2212.10465v1.pdf).

Example:

```
User: Can you write the next few lines of dialogue for this scene:
  Cornell: I know what you're thinking, Dontrell. I can sense your feelings and know exactly what you're going to say or do next. You're thinking about how much you miss your family, and how you wish you could see them again. You're wondering if there's anything you can do to make that happen. And you're also feeling a little guilty, because you know that if you could see them again, it would only be for a short while before they died.
  Dontrell: Cornell, how can you possibly know all that? It's like you can read my mind!
Assistant: Sure, the next dialogue for this scene could be:
  Cornell: I told you, I can sense your feelings. It's like I have a connection to your thoughts and emotions. I'm not sure why or how it works, but ever since we met, I've been able to understand what you're thinking and feeling pretty easily.
  Dontrell: Wow...that's amazing! And a little bit scary too. But it does explain why we've always been so close - even though we've only known each other for a few months.
  Cornell: Yeah, I guess our connection is pretty strong. But don't worry, Dontrell - I'll never use it to manipulate or control you in any way. I promise."
  Dontrell: That's a relief! I was starting to feel a little bit like you could read my mind, and it was kind of creepy. But if you promise not to use your abilities to control me, then I'm okay with it.
  Cornell: I swear, Dontrell. I'll never use my abilities to control or manipulate you in any way. You have my word.
User: And a title?
Assistant: Sure, a title for this dialogue could be:
  Cornell is intuitive. Cornell reads Dontrell's mind.
User: How about a short description?
Assistant: Sure, a short description for this dialogue could be:
  Cornell knows what Dontrell is thinking. He can sense her feelings and know exactly what she is going to say or do next.
User: What would be one theme of this story?
Assistant: One theme of this story could be:
  being intuitive
```

## Usage

The dataset contains one configuration, `dialogue_modeling`, which has a single
text `conversation` feature.

## Source data

The script to synthesize this dataset was originally created by
[ontocord](https://github.com/ontocord) in
[this Colab notebook](https://colab.research.google.com/drive/1Sw3px5dP8whdqT7QMNoqwmqIasZkMbJi?usp=sharing)
and prepared for Hugging Face by
[Jeffrey Quesnelle](https://github.com/jquesnelle/).

## Citation

Please cite our work if you find the resources in this repository useful:

```
@article{ontocord2023sodasynth,
  author    = {ontocord and Jeffrey Quesnelle},
  title     = {SODA Synthetic Dialogue},
  year      = {2023}
}
```
