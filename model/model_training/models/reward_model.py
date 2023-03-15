from typing import Literal

import torch.nn as nn
from transformers import PreTrainedModel


class RewardModel(nn.Module):
    def __init__(self, transformer: PreTrainedModel, pooling: Literal["mean", "last"] = "last"):
        super().__init__()
        self.transformer = transformer
        self.out_proj = nn.Linear(transformer.config.hidden_size, 1)
        self.pooling = pooling

    @property
    def config(self):
        # required for HF-deepspeed integration
        return self.transformer.config

    def forward(self, input_ids, attention_mask=None):
        hiddens = self.transformer(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        if self.pooling == "mean":
            if attention_mask is None:
                pooled = hiddens.mean(dim=1)
            else:
                pooled = (hiddens * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
        elif self.pooling == "last":
            if attention_mask is None:
                pooled = hiddens[:, -1]
            else:
                last_idx = attention_mask.cumsum(dim=1).argmax(dim=1)
                pooled = hiddens.gather(1, last_idx.view(-1, 1, 1).expand(-1, 1, hiddens.size(-1))).squeeze(1)
        else:
            raise ValueError(f"Unknown pooling method: {self.pooling}")
        return self.out_proj(pooled)
