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
      num_bytes: 410246
      num_examples: 1610
  download_size: 105516
  dataset_size: 410246
license: mit
task_categories:
  - question-answering
  - summarization
language:
  - en
tags:
  - Carnegie Mellon University
  - University of Pittsburgh
  - Wikipedia
  - Q&A
pretty_name: Question-Answer Dataset
size_categories:
  - 1K<n<10K
---

# Dataset Card for "cmu_wiki_qa"

A filtered / cleaned version of the http://www.cs.cmu.edu/~ark/QA-data/ Q&A
dataset, which provides manually-generated factoid questions from Wikipedia
articles.

**Acknowledgments**

These data were collected by Noah Smith, Michael Heilman, Rebecca Hwa, Shay
Cohen, Kevin Gimpel, and many students at Carnegie Mellon University and the
University of Pittsburgh between 2008 and 2010.

Their research project was supported by NSF IIS-0713265 (to Smith), an NSF
Graduate Research Fellowship (to Heilman), NSF IIS-0712810 and IIS-0745914 (to
Hwa), and Institute of Education Sciences, U.S. Department of Education
R305B040063 (to Carnegie Mellon).

[More Information needed](https://github.com/huggingface/datasets/blob/main/CONTRIBUTING.md#how-to-contribute-to-the-dataset-cards)
