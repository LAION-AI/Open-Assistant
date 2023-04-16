import os
from argparse import Namespace
from string import Template

import torch
import transformers
from torch import nn
from trainer_rl import argument_parsing
from utils.utils import get_model

conf = argument_parsing()
sft_config = Namespace(**conf.sft_config)
model_name = sft_config.model_name

device = torch.device("cuda:0")

sft_tokenizer = transformers.AutoTokenizer.from_pretrained(sft_config.model_name)

# For llama ...
if sft_tokenizer.pad_token_id == sft_tokenizer.eos_token_id:
    sft_tokenizer.add_special_tokens({"pad_token": "<|padding|>"})

sft_model = get_model(sft_config, sft_tokenizer, pad_vocab_size_to_multiple_of=1)
print('len tokenizer', len(sft_tokenizer))

model_name = model_name.replace("/", "-")

if sft_config.half:
    sft_model = sft_model.half()


sft_model.to(device)
sft_model.eval()


# override forward to return logits
class LogitsModel(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs).logits


sft_model = LogitsModel(sft_model)

inputs = sft_tokenizer("reward model's hash", return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items() if k != 'token_type_ids'}
outputs = sft_model(**inputs)
print(f"{outputs.shape}")

traced_script_module = torch.jit.trace(sft_model, (inputs["input_ids"], inputs["attention_mask"]))

os.makedirs(f"model_store_sft/{model_name}/1", exist_ok=True)
traced_script_module.save(f"model_store_sft/{model_name}/1/traced-model.pt")

config_path = os.path.join("configs", "triton_config_sft.pbtxt")

with open(config_path) as f:
    template = Template(f.read())

config = template.substitute({"model_name": model_name})

with open(f"model_store_sft/{model_name}/config.pbtxt", "w") as f:
    f.write(config)
