---
dataset_info:
  features:
    - name: INSTRUCTION
      dtype: string
    - name: RESPONSE
      dtype: string
    - name: SOURCE
      dtype: string
    - name: METADATA
      dtype: string
  splits:
    - name: train
      num_bytes: 4021291
      num_examples: 16181
  download_size: 2157548
  dataset_size: 4021291
license: mit
task_categories:
  - question-answering
  - text-generation
language:
  - en
tags:
  - ubuntu
  - forum
  - linux
  - chat
pretty_name: Q&A from the Ubuntu Dialogue Corpus
size_categories:
  - 10K<n<100K
---

# Dataset Card for "ubuntu_dialogue_qa"

Filtered the Ubuntu dialogue chatlogs from
https://www.kaggle.com/datasets/rtatman/ubuntu-dialogue-corpus to include Q&A
pairs **ONLY**

**Acknowledgements**

This dataset was ORIGINALLY collected by Ryan Lowe, Nissan Pow , Iulian V.
Serban† and Joelle Pineau. It is made available here under the Apache License,
2.0. If you use this data in your work, please include the following citation:

Ryan Lowe, Nissan Pow, Iulian V. Serban and Joelle Pineau, "The Ubuntu Dialogue
Corpus: A Large Dataset for Research in Unstructured Multi-Turn Dialogue
Systems", SIGDial 2015. URL:
http://www.sigdial.org/workshops/conference16/proceedings/pdf/SIGDIAL40.pdf
