# Sections to train Reward Model (RM)

Trainer code based on huggingface. Should be compatible with deepspeed or accelerate



Requirements

```
wandb
evaluate
datasets
transformers
torch==1.12
```

To train your model run this


```bash
python trainer.py configs/electra-base-dis-webgpt.yml
```


## Dataset

For now we only supports webgpt and summary dataset from OpenAI. Once open-asisstant dataset are available it will be added here.




