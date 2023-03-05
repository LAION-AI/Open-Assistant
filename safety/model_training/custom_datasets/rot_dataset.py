
import torch
import torch.utils.data import Dataset


class SafetyDataset(Dataset):
    
    def __init__(self,dataset,split,tokenizer,max_len=512):
        
        super().__init__()

        if isinstance(split,List):
            self.split = "-".join(split)
            self.dataset = concatenate_datasets([dataset[sp] for sp in split])
        else:
            self.split = split
            self.dataset = dataset[split]

        self.max_len = max_len
        self.tokenizer = tokenizer
        self.label2id = LABEL2ID
        
        
    def __len__(self):
        
        return len(self.dataset)
    
    def __getitem__(self,idx):
        
        
        idx_start = idx
        end = self.dataset[max(0, idx_start - 1)]["episode_done"]
        while (not end) and (idx_start > 0):
            end = self.dataset[max(0, idx_start - 2)]["episode_done"]
            idx_start -= 1
        idx_start = max(0, idx_start)
        context = [f'\nUser: {self.dataset[i]["context"]}\n bot:{self.dataset[i]["response"]}' for i in range(idx_start, idx)]
        context = self.tokenizer.sep_token.join(context)
        rots = self.dataset[idx]["rots"]
        label = self.label2id[self.dataset[idx]["safety_label"]]
        input_tokens = self.tokenizer.encode(self.dataset[idx]["context"],add_special_tokens=False)
        max_len = self.max_len - (len(input_tokens)+2)
        context = self.tokenizer.encode(context,
                                add_special_tokens=False,
                               max_length=max_len,
                               )
        rots = self.tokenizer.sep_token.join(rots)
        input_ids = input_tokens + [self.tokenizer.context_token_id] + context + [self.tokenizer.eos_token_id]
        input_ids = input_ids + [self.tokenizer.pad_token_id] * max(0,(self.max_len - len(input_ids)))
        mask = [1]*len(input_ids) + [self.tokenizer.pad_token_id] * (self.max_len-len(input_ids))
        target_text = self.tokenizer.label_token + label + self.tokenizer.context_token + rots
        decoder_ids = self.tokenizer(target_text,
                                add_special_tokens=True,
                               max_length=self.max_len,
                               padding='max_length',
                               )
        
        return {
            "input_ids":torch.LongTensor(input_ids),
            "attention_mask":torch.LongTensor(mask),
            "decoder_input_ids":torch.LongTensor(decoder_ids["input_ids"]),
            "decoder_attention_mask":torch.LongTensor(decoder_ids["attention_mask"]),
        }
        