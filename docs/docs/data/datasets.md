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

Fork the
`OpenAssistant`[repository](https://github.com/LAION-AI/Open-Assistant). To do
this, click the link to the repository and click "Fork" in the upper-right
corner. You should get an option to fork to your account, provided you are
signed into Github.

After you fork, clone the repository locally. You can do so as follows:

```bash
git clone git@github.com:<your_github_username>/OpenAssistant.git
cd OpenAssistant  # enter the directory
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
git remote add origin git@github.com:<your_github_username>/OpenAssistant.git
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

Please do not make changes on the master branch!

:::

Always make sure you're on the right branch with the following command:

```
git branch
```

The correct branch will have a asterisk \* in front of it.

### 2. **Create a development environment**

You can make an environment in any way you choose to. We highlight two possible
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
Add any extra depen
