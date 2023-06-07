---
dataset_info:
  features:
    - name: TEXT
      dtype: string
    - name: SOURCE
      dtype: string
    - name: METADATA
      struct:
        - name: ch_num
          dtype: string
        - name: title
          dtype: string
  splits:
    - name: train
      num_bytes: 27856275
      num_examples: 361
  download_size: 11507610
  dataset_size: 27856275
license: mit
task_categories:
  - text-generation
language:
  - th
size_categories:
  - n<1K
---

# Dataset Card for "tlcv2.0_oa"

Thai Literature Corpora (TLC): Corpora of machine-ingestible Thai classical
literature texts by Jitkapat Sawatphol (Faculty of Arts, Chulalongkorn
University).

This project use
[Thai Literature Corpora (TLC) v2.0](https://attapol.github.io/tlc.html). All
text are from old Thai book that out of copyright (or public domain).
