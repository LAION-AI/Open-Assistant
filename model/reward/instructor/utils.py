import re
from torch.utils.data import Subset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

re_reference_remove = re.compile(r'\[([0-9])+\]|\[([0-9])+,([0-9])+\]')

def webgpt_return_format(row):
    if row['score_0'] >= row['score_1']:
        # remove this to prevent information leak, since we are not using reference
        return {
                'question': row['question']['full_text'],
                     'pos': re_reference_remove.sub('', row['answer_0']),
                     'neg': re_reference_remove.sub('', row['answer_1'])
                }

    return {
            'question': row['question']['full_text'],
                 'pos': re_reference_remove.sub('', row['answer_1']),
                 'neg': re_reference_remove.sub('', row['answer_0'])
            }


def get_tokenizer(tokenizer_name):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if 'galactica' in tokenizer_name:
        tokenizer.add_special_tokens({'pad_token':'<pad>', 'eos_token': '</s>' })

    return tokenizer



def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(list(range(len(dataset))), 
        test_size=val_split, random_state=666, shuffle=True)
    # [3879, 11479, 8341, 9177, 10798, 18177, 5735, 15669, 4837, 2760]
    print(val_idx[:10])
    # [13582, 5919, 11875, 7373, 19135, 13706, 8555, 15788, 15005, 15209]
    print(train_idx[:10])
    return Subset(dataset, train_idx), Subset(dataset, val_idx)

