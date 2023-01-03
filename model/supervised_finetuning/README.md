# Train using supervised examples

Requirements

```
wandb
evaluate
datasets
transformers
torch
```

Start training reward model

```bash
python trainer.py --configs defaults galactica-125
```

## Dataset

For now we only support webgpt and summary dataset from OpenAI. Once
open-asisstant dataset are available it will be added here.

## Model

TBD

## Results

Experimental results in wandb
[here](https://wandb.ai/sanagnos/supervised-finetuning?workspace=user-sanagnos).

## TODOS

- decide on a model
- add special token to declare prompt and reply. Do nto freeze the weights for
  these
- Merge utils etc with reward model
