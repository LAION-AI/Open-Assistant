'''
    author: theblackcat102

    A list of rank based dataset for training using rank loss

    Some nice features to have

    [ ] 

'''
import os
import glob
import json
import numpy as np
from torch.utils.data import Dataset
from datasets import load_dataset

class CollateFN():
    def __init__(self, tokenizer, max_length=400) -> None:
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, batch):
        prompts = []
        pos_sentences = []
        neg_sentences = []
        for prompt, pairs in batch:
            for (pos, neg) in pairs:
                prompts.append(prompt)
                pos_sentences.append(pos)
                neg_sentences.append(neg)

        batch = [self.tokenizer(prompts, pos_sentences, return_tensors='pt', max_length=self.max_length, padding=True, truncation=True),\
                self.tokenizer(prompts, neg_sentences, return_tensors='pt', max_length=self.max_length, padding=True, truncation=True)]
        return batch

class WebGPT(Dataset):

    def __init__(self) -> None:
        super().__init__()

        dataset = load_dataset("openai/webgpt_comparisons")
        questions = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2question = {}
        for row in dataset['train']:
            question = row['question']['full_text']
            if question not in self.index2question:
                self.index2question[len(self.index2question)] = question

            if question not in questions:
                questions[question] = []

            if row['score_0'] > row['score_1']:
                # not going to risk it
                questions[question].append((
                    row['answer_0'], row['answer_1']
                ))
            else:
                questions[question].append((
                    row['answer_1'], row['answer_0']
                ))

        self.questions = questions

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        rows = self.questions[question]
        # optimize the format later
        return question, rows




class HFSummary(Dataset):
    '''
        Human feedback data from OpenAI
        https://github.com/openai/summarize-from-feedback

            >> azcopy copy "https://openaipublic.blob.core.windows.net/summarize-from-feedback/dataset/*" . --recursive
        
        choice : 0 or 1

    '''
    def __init__(self, split='train',
        path='summarize-from-feedback/comparisons/*.json',
        conf_threshold=-1,
        max_comparison_per_sample=5) -> None:
        super().__init__()
        assert split in ('train', 'valid1', 'valid2', 'test')
        summaries = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2summary = {}
        self.max_comparison_per_sample = max_comparison_per_sample
        for jsonl_file in glob.glob(path):
            with open(jsonl_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if data['split'] != split:
                        continue
                    if 'extra' in data and \
                        'confidence' in data['extra'] and \
                        conf_threshold > data['extra']['confidence']:
                        print('skipping {}'.format(data['info']['id']))
                        continue

                    if 'article' in data['info']:
                        context = data['info']['article']
                    elif 'post' in data['info']:
                        context = data['info']['post']

                    if context not in self.index2summary:
                        self.index2summary[len(self.index2summary)] = context
                    
                    if context not in summaries:
                        summaries[context] = []

                    pos, neg = (0, 1) if data['choice'] == 0 else (1, 0)
                    summaries[context].append((
                        data['summaries'][pos]['text'],
                        data['summaries'][neg]['text']
                    ))

        self.summaries = summaries

    def __len__(self):
        return len(self.index2summary)

    def __getitem__(self, index):
        context = self.index2summary[index]
        # return pairs of comparison
        rows = self.summaries[context]
        # pair very big
        # we are going to do some sampling
        # not optimal but good for now
        valid_idx = np.random.choice(len(rows), self.max_comparison_per_sample)
        # optimize the format later
        return context, [ r for idx, r in enumerate(rows) if idx in valid_idx ]


