import os
from argparse import Namespace
from string import Template

import torch
import transformers
from torch import nn
from trainer_rl import argument_parsing
from utils.utils import get_model

conf = argument_parsing()
rank_config = Namespace(**conf.rank_config)
model_name = rank_config.model_name

device = torch.device("cuda:0")

rank_tokenizer = transformers.AutoTokenizer.from_pretrained(rank_config.model_name)

# TODO Load directly into torch.float16
rank_model = get_model(rank_config, rank_tokenizer).to(device)

model_name = model_name.replace("/", "-")

rank_model = rank_model.half()

rank_model.to(device)
rank_model.eval()


# override forward to return logits
class LogitsModel(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs).logits[:, 0]


rank_model = LogitsModel(rank_model)

inputs = rank_tokenizer("reward model's hash", return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
print(f"{rank_model(**inputs)=}")

traced_script_module = torch.jit.trace(rank_model, (inputs["input_ids"], inputs["attention_mask"]))

os.makedirs(f"model_store/{model_name}/1", exist_ok=True)
traced_script_module.save(f"model_store/{model_name}/1/traced-model.pt")

config_path = os.path.join("configs", "triton_config.pbtxt")

with open(config_path) as f:
    template = Template(f.read())

config = template.substitute({"model_name": model_name})

with open(f"model_store/{model_name}/config.pbtxt", "w") as f:
    f.write(config)
