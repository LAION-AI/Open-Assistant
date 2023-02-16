# Datasets

The datasets for this project are currently hosted as loading scripts on the
[Open-Assistant organization](https://huggingface.co/OpenAssistant) the Hugging
Face Hub. Each of them can be loaded by first installing the 🤗 Datasets
library:

```bash
python -m pip install datasets
```

and then running:

```python
from datasets import load_dataset

dataset = load_dataset("OpenAssistant/{dataset-name}")
```

We use this GitHub repository to accept new submissions and standardize quality
control. See the instructions below if you'd like to contribute a new dataset to
the project.

## Adding a new dataset

### 0. Pre-Requisites

Install Git and create a GitHub account prior to implementing a dataset; you can
follow instructions to install Git
[here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

You will also need at least Python 3.8+. If you are installing Python, we
recommend downloading
[Anaconda](https://docs.anaconda.com/anaconda/install/index.html) to curate a
python environment with necessary packages. **We strongly recommend Python 3.8+
for stability**.

### 1. **Fork the OpenAssistant repository**

Fork the [OpenAssistant repository](https://github.com/LAION-AI/Open-Assistant).
To do this, click the link to the repository and click "Fork" in the upper-right
corner. You should get an option to fork to your account, provided you are
signed into Github.

After you fork, clone the repository locally. You can do so as follows:

```bash
git clone git@github.com:<your_github_username>/Open-Assistant.git
cd Open-Assistant  # enter the directory
```

Next, you want to set your `upstream` location to enable you to push/pull (add
or receive updates). You can do so as follows:

```bash
git remote add upstream git@github.com:LAION-AI/Open-Assistant.git
```

You can optionally check that this was set properly by running the following
command:

```bash
git remote -v
```

The output of this command should look as follows:

```bash
origin  git@github.com:<your_github_username>/Open-Assistant.git (fetch)
origin  git@github.com:<your_github_username>/Open-Assistant.git (push)
upstream        git@github.com:LAION-AI/Open-Assistant.git (fetch)
upstream        git@github.com:LAION-AI/Open-Assistant.git (push)
```

If you do NOT have an `origin` for whatever reason, then run:

```bash
git remote add origin git@github.com:<your_github_username>/Open-Assistant.git
```

The goal of `upstream` is to keep your repository up-to-date to any changes that
are made officially to the OpenAssistant repo. You can do this as follows by
running the following commands:

```
git fetch upstream
git pull
```

Provided you have no _merge conflicts_, this will ensure the repo stays
up-to-date as you make changes. However, before you make changes, you should
make a custom branch to implement your changes.

You can make a new branch as such:

```
git checkout -b <dataset_name>
```

:::caution

Please do not make changes on the main branch!

:::

Always make sure you're on the right branch with the following command:

```
git branch
```

The correct branch will have a asterisk \* in front of it.

### 2. **Create a development environment**

You can make an environment in any way you choose. We highlight two possible
options:

#### 2a) Create a conda environment

The following instructions will create an Anaconda `openassistant` environment.

- Install [anaconda](https://docs.anaconda.com/anaconda/install/) for your
  appropriate operating system.
- Run the following command while in the `biomedical` folder (you can pick your
  python version):

```bash
conda create -n openassistant python=3.8  # Creates a conda env
conda activate openassistant  # Activate your conda environment
cd openassistant
pip install -r dev-requirements.txt # Install this while in the openassistant folder
```

You can deactivate your environment at any time by either exiting your terminal
or using `conda deactivate`.

#### 2b) Create a venv environment

Python 3.3+ has venv automatically installed; official information is found
[here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

```
python3 -m venv <your_env_name_here>
source <your_env_name_here>/bin/activate  # activate environment
cd openassistant
pip install -r dev-requirements.txt # Install this while in the openassistant folder
```

Make sure your `pip` package points to your environment's source.

### 3. Prepare a folder in `datasets` for your dataloader

Make a new directory within the `openassistant/datasets` directory:

```bash
mkdir openassistant/datasets/<dataset_name>
```

**NOTE**: Please use snake_case, i.e. lowercase letters and underscores when
choosing a `<dataset_name>`.

Add an `__init__.py` file to this directory:

```bash
touch openassistant/datasets/<dataset_name>/__init__.py
```

Next, copy the `template.py` script and `hub.py` module of `templates` into your
dataset folder. The `template.py` script has "TODOs" to fill in for your
dataloading script:

```bash
cp templates/hub.py openassistant/datasets/<dataset_name>/
cp templates/template.py openassistant/datasets/<dataset_name>/<dataset_name>.py
```

#### (Optional) Prepare local dataset files

If your dataset files aren't publicly available via URLs (e.g. because you
implemented a web scraper), you'll need to implement some extra logic to store
and prepare the data locally prior to implementing a loading script in 🤗
Datasets.

To do so, first copy the template script for dataset creation:

```bash
cp templates/prepare.py openassistant/datasets/<dataset_name>/
```

Next, implement any logic that is needed to prepare a local version of the
dataset files (by convention we store them in `datasets/<dataset_name>/data/`).
Add any extra dependencies to a `requirements.txt` file and provide instructions
on how to prepare the dataset files in a README:

```bash
touch openassistant/datasets/<dataset_name>/requirements.txt
cp templates/README.py openassistant/datasets/<dataset_name>/
```

**Note:** Do not commit any dataset files to the OpenAssistant repo - all data
will be hosted on the Hugging Face Hub. This step is needed for the project's
data admins to be able to replicate the dataset creation process before pushing
to the Hub.

### 4. Implement your dataset

To implement your dataloader, you will need to follow `template.py` and fill in
all necessary TODOs. There are three key methods that are important:

- `_info`: Specifies the schema of the expected dataloader
- `_split_generators`: Downloads and extracts data for each split (e.g.
  train/val/test) or associate local data with each split.
- `_generate_examples`: Create examples from data that conform to each schema
  defined in `_info`.

For the `_info_` function, you will need to define `features` for your
`DatasetInfo` object. For each dataset config, choose the right schema from our
list of examples. You can find the schemas in the
[schemas directory](https://github.com/LAION-AI/Open-Assistant/blob/main/docs/docs/data/schemas.mdx).

You will use this schema in the `_generate_examples` return value.

Populate the information in the dataset according to this schema; some fields
may be empty.

#### Example scripts

TODO

#### Running & debugging

You can run your data loader script during development by appending the
following statement to your code
([templates/template.py](https://github.com/LAION-AI/Open-Assistant/blob/main/openassistant/templates/template.py)
already includes this):

```python
if __name__ == "__main__":
    datasets.load_dataset(__file__)
```

If you want to use an interactive debugger during development, you will have to
use `breakpoint()` instead of setting breakpoints directly in your IDE. Most
IDEs will recognize the `breakpoint()` statement and pause there during
debugging. If your preferred IDE doesn't support this, you can always run the
script in your terminal and debug with `pdb`.

### 5. Check if your dataloader works

Make sure your dataset is implemented correctly by checking in python the
following commands:

```python
from datasets import load_dataset

data = load_dataset("openassistant/datasets/<dataset_name>/<dataset_name>.py", name="<dataset_name>_<schema>")
```

Run these commands from the top level of the `OpenAssistant` repo.

### 6. Create a dataset card

Copy and fill out the template dataset card:

```bash
cp templates/dataset_card.md openassistant/datasets/<dataset_name>/README.md
```

### 7. Format your code

From the main directory, run the code quality checks via the following command:

```
pre-commit run --all-files
```

This runs the black formatter, isort, and lints to ensure that the code is
readable and looks nice. Flake8 linting errors may require manual changes.

### 8. Commit your changes

First, commit your changes to the branch to "add" the work:

```
git add openassistant/datasets/<dataset_name>/*.py
git commit -m "A message describing your commits"
```

Then, run the following commands to incorporate any new changes in the master
branch of datasets as follows:

```
git fetch upstream
git rebase upstream/main
```

**Run these commands in your custom branch**.

Push these changes to **your fork** with the following command:

```
git push -u origin <dataset_name>
```

### 9. **Make a pull request**

Make a Pull Request to implement your changes on the main repository
[here](https://github.com/LAION-AI/Open-Assistant/pulls). To do so, click "New
Pull Request". Then, choose your branch from your fork to push into "base:main".

When opening a PR, please link the
[issue](https://github.com/LAION-AI/Open-Assistant/issues) corresponding to your
dataset using
[closing keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
in the PR's description, e.g. `resolves #17`.

## [Admins] Uploading a dataset to the Hugging Face Hub

Uploading a new dataset from `openassistant/datasets/<dataset_name>` to the
Hugging Face Hub typically involves the following steps:

1. Setup
2. Create a new dataset repository
3. Copy a dataset loading script and dataset card
4. Upload to the Hub

### 1. Setup

To upload a dataset to the OpenAssistant organization, you first need to:

- Create a [Hugging Face account](https://huggingface.co/join) (it's free)
- Join the [OpenAssistant organization](https://huggingface.co/OpenAssistant) by
  clicking on the _Request to join this org_ button on the top right-hand side

Next, check that you're correctly logged in and that `git-lfs` is installed so
that the dataset can be uploaded. To log in, create a **write access token**
that can be found under your Hugging Face profile (icon in the top right corner
on [hf.co](http://hf.co/), then Settings -> Access Tokens -> User Access Tokens
-> New Token. Alternatively, you can go to
[your token settings](https://huggingface.co/settings/tokens) directly.

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

Next, let's make sure that `git-lfs` is correctly installed. To do so, simply
run:

```bash
git-lfs -v
```

The output should show something like
`git-lfs/2.13.2 (GitHub; linux amd64; go 1.15.4)`. If your console states that
the `git-lfs` command was not found, please make sure to install it
[here](https://git-lfs.github.com/) or simply via:

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

Follow [this guide](https://huggingface.co/docs/datasets/upload_dataset) for
instructions on creating a new dataset repo on the Hub. Use the same snake_case
name as the dataset in `openassistant/datasets/<dataset_name>`.

Once you've created the dataset repo, clone it by running:

```bash
git clone https://huggingface.co/datasets/OpenAssistant/<dataset_name>
cd <dataset_name>
```

### 3. Copy a dataset loading script and dataset card

Next, copy the loading script and dataset card to your repo:

```bash
cp openassistant/datasets/<dataset_name>/<dataset_name>.py .
cp openassistant/datasets/<dataset_name>/README.md .
```

#### (Optional) Prepare local dataset files

If the dataset files of `openassistant/datasets/<dataset_name>` aren't public,
you'll need to run the `openassistant/datasets/<dataset_name>/prepare.py` script
to create them. Store them in the same directory that is specified by the
loading script (`data` by default).

### 4. Upload to the Hub

Once the dataset script and card are ready, use Git to push them to the Hub
(along with any data files you may need).

At this point, you can load the dataset by running:

```python
from datasets import load_dataset

load_dataset("OpenAssistant/{dataset_name}")
```

Congratulations - you've now added a dataset to the OpenAssistant org!
