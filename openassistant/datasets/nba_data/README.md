# Dataset preparation instructions for {dataset_name}

## Setup

install deps from requirements.txt

## Usage

<<<<<<< HEAD
Run 
    data = load_dataset("openassistant/datasets/nba_data/data",name="raw_data2022.csv") 
or
    data = load_dataset("openassistant/datasets/nba_data/nba_data.py", name="nba_data")
from the top level of the repo.
NOTE: the second one currently returns an empty dataset dict but could be a helpful start for someone else who needs a loading script with their dataset.

At the least, this will give people a place to upload their data, so others can see what has already been collected.

If you would want to generate more csv data for the nba specifically, run prepare.py and input the season you want.