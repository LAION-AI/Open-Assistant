import torch
from transformers import AutoModel


class RankGenModel(torch.nn.Module):
    def __init__(self, model_name):
        super().__init__()
        self.rankgen_hf_hub = model_name
        assert model_name in [
            "kalpeshk2011/rankgen-t5-xl-all",
            "kalpeshk2011/rankgen-t5-xl-pg19",
            "kalpeshk2011/rankgen-t5-base-all",
            "kalpeshk2011/rankgen-t5-large-all",
        ]
        self.model = AutoModel.from_pretrained(self.rankgen_hf_hub, trust_remote_code=True)

    def forward(self, prefixes, suffixes):
        # print(list(self.model.parameters()))
        # raise Exception("stop")
        embedded_prefixes = self.model(**prefixes)
        embedded_suffixes = self.model(**suffixes)
        # take dot product of each row independently
        dot_products = torch.sum(embedded_prefixes * embedded_suffixes, dim=1)

        # print(f"{embedded_prefixes.shape=}, {embedded_suffixes.shape=}, {prefixes['input_ids'].shape=}, {suffixes['input_ids'].shape=}, {embedded_prefixes=}, {embedded_suffixes=}, {dot_products=}")
        # raise Exception("stop")
        return dot_products
