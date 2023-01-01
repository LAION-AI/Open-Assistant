# Sections to train Reward Model (RM)

Trainer code based on huggingface. Compatible with deepspeed or accelerate


Requirements

```
wandb
evaluate
datasets
transformers
torch==1.12
```

Start training


```bash
python trainer.py configs/electra-base-dis-webgpt.yml
```


## Dataset

For now we only supports webgpt and summary dataset from OpenAI. Once open-asisstant dataset are available it will be added here.

## Model

Check out configs

```
Open-Assistant/model/reward/instructor/configs/
    bloomz-560m.yml
    electra-base-dis-webgpt.yml
    galactica-125m.yml
    galactica-1b.yml
```

You can add new huggingface model as you want.
