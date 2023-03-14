# Python Code and Test Generation Datasets

This folder contains two notebooks.

One will download the HumanEval and MBPP datasets used for Microsoft CodeT for
tuning a model for Python code generation from function docstrings, augment the
data into prompt and solution pairs and write them to `.jsonl` files.

The other will download the data used for Microsoft CodeT for tuning a model for
Python test generation from corresponding function docstrings, augment the data
into prompt and solution pairs and write them to `.jsonl` files.

All datasets are then uploaded to HuggingFace Hub, the code generation data is
uploaded separately from the test generation data.

## Requirements

Both notebooks require the library `requests`.
