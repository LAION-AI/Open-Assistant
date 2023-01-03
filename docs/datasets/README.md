# Datasets

The datasets for this project are currently hosted under the [Open-Assistant organization](https://huggingface.co/OpenAssistant) the Hugging Face Hub. Each of them can be loaded by first installing the 🤗 Datasets library:

```bash
python -m pip install datasets
```

and then running:

```python
from datasets import load_dataset

dataset = load_dataset("OpenAssistant/<dataset-name>")
```

See the instructions below if you'd like to contribute a new dataset to the project.

## Uploading a dataset to the Hugging Face Hub

Adding a new dataset for the OpenAssistant project typically involves the following steps:

1. Setup
2. Create a new dataset repository
3. Create a dataset loading script and dataset card
4. Upload to the Hub

### 1. Setup

To upload a dataset to the OpenAssistant organization, you first need to:

* Create a [Hugging Face account](https://huggingface.co/join) (it's free)
* Join the [OpenAssistant organization](https://huggingface.co/OpenAssistant) by clicking on the _Request to join this org_ button on the top right-hand side

By default, your [role](https://huggingface.co/docs/hub/organizations-security#access-control-in-organizations) in the organization is `contributor`, which gives you write access to any datasets that you create (and only those). If you'd like to make changes to other datasets, [open a discussion or Hub pull request](https://huggingface.co/docs/hub/repositories-pull-requests-discussions).

Next, check that you're correctly logged in and that `git-lfs` is installed so that the dataset can be uploaded. To log in, create a **write access token** that can be found under your Hugging Face profile (icon in the top right corner on [hf.co](http://hf.co/), then Settings -> Access Tokens -> User Access Tokens -> New Token. Alternatively, you can go to [your token settings](https://huggingface.co/settings/tokens) directly.

Once you've created a token, run:

```bash
huggingface-cli login
```

in a terminal, or case you're working in a notebook

```python
from huggingface_hub import notebook_login

notebook_login()
```

You can then copy-paste your token to log in locally.

Next, let's make sure that `git-lfs` is correctly installed. To do so, simply run:

```bash
git-lfs -v
```

The output should show something like `git-lfs/2.13.2 (GitHub; linux amd64; go 1.15.4)`. If your console states that the `git-lfs` command was not found, please make sure to install it [here](https://git-lfs.github.com/) or simply via:

```bash
sudo apt-get install git-lfs
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

The final step of the setup is to install the 🤗 Datasets library by running:

```bash
python -m pip install datasets
```

### 2. Create a new dataset repository

We've created a [Gradio application](https://huggingface.co/spaces/OpenAssistant/dataset-generator) on Hugging Face Spaces that will create a new dataset repository for you with the following template files:

* A dataset loading script
* A dataset card

Simply provide the name of the new dataset and your access token from Step 1, and you're good to go!

### 3. Create a dataset loading script

If you've followed Step 2, a template dataset loading script will have been created in your new dataset repository. Edit the script according to [this guide](https://huggingface.co/docs/datasets/dataset_script). Then fill out the missing details in the dataset card (the `README.md` file)

### 4. Upload to the Hub

Once the dataset script and card are ready, use Git to push them to the Hub (along with any data files you may need).

At this point, you can load the dataset by running:

```python
from datasets import load_dataset

load_dataset("OpenAssistant/my_dataset")
```

Congratulations - you've now added a dataset to the Hub!

