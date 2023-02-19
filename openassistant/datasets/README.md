# **Datasets**

This folder contains datasets loading scripts that are used to train
OpenAssistant. The current list of datasets can be found
[here](https://docs.google.com/spreadsheets/d/1NYYa6vHiRnk5kwnyYaCT0cBO62--Tm3w4ihdBtp4ISk).

## **Adding a New Dataset**

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

## **Creating a Dataset on Hugging Face**

To create a new dataset on Hugging Face, follow these steps:

#### 1. Convert your dataset file(s) to the Parquet format using the [pandas](https://pandas.pydata.org/) library:

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

- in Jupyter notebook (cuurently does not work in
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

#### 5. Update the `README.md` file

Update the `README.md` file of your dataset by visiting this link:
https://huggingface.co/datasets/your_huggingface_name/dataset_name/edit/main/README.md
(paste your HuggingFace name and dataset)

## **Making a Pull Request**

#### 1. Fork this repository

#### 2. Create a new branch in your fork

#### 3. Add your dataset to the repository

- Create a folder with the name of your dataset.
- Add a loading script that loads your dataset from HuggingFace, for example:

  ```python
  from datasets import load_dataset

  if __name__ == "__main__":
      ds = load_dataset("your_huggingface_name/dataset_name")
      print(ds["train"])
  ```

- Optionally, add any other files that describe your dataset and its creation,
  such as a README, notebooks, scrapers, etc.

#### 4. Stage your changes and run the pre-commit hook

```bash
pre-commit run
```

#### 5. Submit a pull request

- Submit a pull request and include a link to the issue it resolves in the
  description, for example: `Resolves #123`
