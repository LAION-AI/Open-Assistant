import os
from typing import Literal, Optional, Union

import torch.nn as nn
from models import get_specific_model
from transformers import PretrainedConfig, PreTrainedModel


class RewardModelConfig(PretrainedConfig):
    base_model_name: str
    pooling: Literal["mean", "last"]
    model_type = "reward_model"
    hidden_size: int | None = None  # deepspeed reads this

    def __init__(
        self,
        base_model_name: str = None,
        pooling: Literal["mean", "last"] = "last",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.base_model_name = base_model_name
        self.pooling = pooling or "last"

    @classmethod
    def from_pretrained(
        cls, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[str] = None, **kwargs
    ):
        config, model_kwargs = super().from_pretrained(pretrained_model_name_or_path, **kwargs)
        if cache_dir:
            model_kwargs["cache_dir"] = cache_dir
        return config, model_kwargs


class RewardModel(PreTrainedModel):
    config_class = RewardModelConfig

    def __init__(self, config: RewardModelConfig, cache_dir: Optional[str] = None):
        super().__init__(config=config)

        transformer = get_specific_model(
            config.base_model_name,
            seq2seqmodel=False,
            without_head=True,
            cache_dir=cache_dir,
        )

        self.transformer = transformer
        self.out_proj = nn.Linear(transformer.config.hidden_size, 1)
        self.pooling = config.pooling
        self.config.hidden_size = transformer.config.hidden_size

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
