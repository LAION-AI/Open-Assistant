'''
    HFSummary

        I want to train a multi regression model on axis_evals dataset mainly we can estimate the score of these score

         - {"overall": "6", "accuracy": "6", "coverage": "6", "coherence": "7"}

        Should be better than just a preference score

'''
import os
import json
import random
import torch
import numpy as np
from dataset import load_dataset
from torch.utils.data import Dataset


