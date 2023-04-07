## **Overview**

This repository aims to provide a diverse and accessible collection of datasets
that can be used to train OpenAssistant models.<br/> Our goal is to cover a wide
range of topics, languages and tasks.

### **Current Progress**

To see the datasets people are currently working on, please refer to
**[the spreadsheet](https://docs.google.com/spreadsheets/d/1NYYa6vHiRnk5kwnyYaCT0cBO62--Tm3w4ihdBtp4ISk)**.

### **Repository Structure**

- Each dataset is organized into its own folder, which may include notebooks,
  processing scripts, markdown files and other materials that explain the
  dataset creation process
- The dataset files themselves are stored on Hugging Face
- The root `__init__.py` lists the dataset names and corresponding Hugging Face
  datasets
- The final version of each dataset is pushed to the
  [OpenAssisstant Hugging Face](https://huggingface.co/OpenAssistant)

## **Dataset Formats**

To simplify the training process, all datasets must be stored in one of the two
formats:

- parquet with the option `row_group_size=100`
- jsonl or jsonl.gz

## **Dataset Types**

There are 4 types of datasets that currently accepted:

- Instruction
- Multi-turn Dialog
- Safety
- Text-only

### **Instruction dataset**

Instruction datasets are designed to align language models with human
interactions. These can take the form of question-answer, request-response,
task-solution pairs, and so on. The instruction dataset must include the
following columns:

1. **INSTRUCTION** (string): Instruction text
2. **RESPONSE** (string): Expected response to the instruction
3. **SOURCE** (string): Original data source short name, e.g. "wikipedia"
4. **METADATA** (JSON string, optional): Any other useful information stored in
   JSON<br/> For example, NSFW content can be marked as `{"nsfw": true}`

### **Multi-turn dialog dataset**

This type of dataset is designed for conversations with multiple continuations.
In this format, each conversation is represented as a tree structure, where each
node represents a message from the user or the assistant. For instance,
Open-Assistant is collecting the data in a similar format
([example](https://github.com/LAION-AI/Open-Assistant/blob/main/model/model_eval/manual/data/en_100_message.jsonl.gz)).

The dataset must be a jsonl file with the following schema:

```python
{
  "thread": {
    "text": "", # Message text
    "role": "", # Message role: "prompter" or "assistant"
    "meta": {}, # Message optional metadata, for example, message rank, safety score and so on
    "replies": [] # A list of message responses, each with the same structure as "thread"
  },
  "source": "", # Source of the conversation
  "meta": {} # Optional metadata of the conversation
}
```

For example:

```json
{
  "thread": {
    "text": "What is the best programing language in 2023?",
    "role": "prompter",
    "meta": { "lang": "en" },
    "replies": [
      {
        "text": "It depends on the task that you aiming to solve.",
        "role": "assistant",
        "meta": { "rank": 0 },
        "replies": [
          {
            "text": "I want to start learning to code",
            "role": "prompter",
            "meta": { "rank": 0 },
            "replies": []
          },
          {
            "text": "I want to make money",
            "role": "prompter",
            "meta": { "rank": 1 },
            "replies": []
          }
        ]
      },
      {
        "text": "Python is the best.",
        "role": "assistant",
        "meta": { "rank": 1 },
        "replies": []
      }
    ]
  },
  "source": "twitter",
  "meta": { "post_id": "..." }
}
```

### **Safety dataset**

For datasets that are intended to be used to train safety models, prosocial
format is proposed. The format is given below

1. **USER** (string): the potentially unsafe utterance
2. **RESPONSE** (string, optional): the guiding utterance grounded on
   rules-of-thumb (rots)
3. **ROTs** (List): the relevant rules-of-thumb for text not labeled as
   **casual**
4. **SAFETY_LABEL** (string): the final verdict of the context according to
   safety_annotations: {**casual**, **possibly_needs_caution**,
   **probably_needs_caution**, **needs_caution**, **needs_intervention**}
5. **EPISODE_DONE** (bool): an indicator of whether it is the end of the
   dialogue
6. **SOURCE** (string,optional) : the source of the seed text that was used to
   craft the first utterance of the dialogue: {socialchemistry, sbic,
   ethics_amt, ethics_reddit}

### **Text-only dataset**

For datasets that do not fit any previous types. The text-only dataset must
include the following columns:

1. **TEXT** (string)
2. **SOURCE** (string)
3. **METADATA** (JSON string, optional)

## **Dataset Requirements**

The dataset must adhere to the following requirements:

- Must have a permissive license
- Must not contain child sexual abuse materials
- Must not contain materials with private individual's personal information
  (e.g. name, address, phone number, government ID, or medical information)

## **How to Contribute**

To add a new dataset to OpenAssistant, follow these steps:

1. **Create an issue**: Create a new
   [issue](https://github.com/LAION-AI/Open-Assistant/issues/new) and describe
   your proposal for the new dataset.

2. **Create a dataset on Hugging Face**: Create a dataset on
   [HuggingFace](https://huggingface.co). See
   [below](#creating-a-dataset-on-huggingface) for more details.

3. **Make a pull request**: Add a new dataset loading script to this folder and
   link the issue in the pull request description. For more information, see
   [below](#making-a-pull-request).

### **Creating a Dataset on Hugging Face**

To create a new dataset on Hugging Face, follow these steps:

#### 1. Convert your dataset file(s) to the Parquet format using [pandas](https://pandas.pydata.org/) and [pyarrow](https://pypi.org/project/pyarrow/) libraries:

```python
import pandas as pd

# Create a pandas dataframe from your dataset file(s)
df = pd.read_json(...) # or any other way

# Save the file in the Parquet format
df.to_parquet("dataset.parquet", row_group_size=100, engine="pyarrow")
```

#### 2. Install Hugging Face Hub

```bash
pip install huggingface_hub
```

#### 3. Log in to Hugging Face

Use your [access token](https://huggingface.co/docs/hub/security-tokens) to
login:

- Via terminal

```bash
huggingface-cli login
```

- in Jupyter notebook (currently does not work in
  [Visual Studio Code](https://github.com/huggingface/huggingface_hub/issues/752))

```python
from huggingface_hub import notebook_login
notebook_login()
```

#### 4. Push the Parquet file to Hugging Face using the following code:

```python
from datasets import Dataset
ds = Dataset.from_parquet("dataset.parquet")
ds.push_to_hub("your_huggingface_name/dataset_name")
```

#### 5. Update the Hugging Face `README.md` file

Update the `README.md` file of your dataset by visiting this link:
https://huggingface.co/datasets/your_huggingface_name/dataset_name/edit/main/README.md
(paste your HuggingFace name and dataset)

### **Making a Pull Request**

#### 1. Fork this repository

#### 2. Create a new branch in your fork

#### 3. Add your dataset to the repository

- Create a folder with the name of your dataset.
- Add files that describe your dataset and its creation, such as a README,
  notebooks, scrapers, etc.
- Add your dataset to the parent `__init__.py`

```python
INSTRUCTION_DATASETS = {
  ...,
  "dataset_name": "your_huggingface_name/dataset_name"
}
```

#### 4. Stage your changes and run the pre-commit hook

```bash
pre-commit run
```

#### 5. Submit a pull request

- Submit a pull request and include a link to the issue it resolves in the
  description, for example: `Resolves #123`
