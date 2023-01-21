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

Normally you should be able to add new models in configs/config.yml

```
your-model-name:
  learning_rate: 2e-6
  model_name: <huggingface model name>
  weight_decay: 0.01
  max_length: 812
  warmup_steps: 600
  gradient_checkpointing: false
  gradient_accumulation_steps: 5
  per_device_train_batch_size: 4
  per_device_eval_batch_size: 4
```

```
python trainer.py --configs defaults your-model-name
```

However, if the model of your choice doesn't have pad_token, eos_token,
sep_token, you have to update utils.py `get_tokenizer` to use the right token.

## Deepspeed support

You can edit the configs/zero_config.json and use any stage you wish. The
current config uses zero-stage 3. For more details on how to setup the config
checkout [this page](https://www.deepspeed.ai/tutorials/zero/)

Once you are satisfy with your deepzero config, you can add --deepspeed flag at
the end to trigger deepspeed

```
python trainer.py --configs defaults your-model-name --deepspeed
```

## Dataset choices

To specify which translation pair for
[WMT](https://huggingface.co/datasets/wmt19) and
[TED Talk](https://huggingface.co/datasets/ted_talks_iwslt) translation simply
add the supported language pair at the postfix

```
  datasets:
    - wmt2019_zh-en
    - wmt2019_ru-en
    - wmt2019_de-en
    - ted_trans_nl-en
    - ted_trans_de-ja
```

Currently only these languages are supported via prompt translation:

```
ar,de,fr,en,it,nl,tr,ru,ms,ko,ja,zh
```

## Results

Experimental results in wandb
[here](https://wandb.ai/sanagnos/supervised-finetuning?workspace=user-sanagnos).

## TODOS

- decide on a model
- Merge utils etc with reward model
- Casual Modelling for GPT-JT does not leverage the bidirectional mask for the
  prompt? (https://huggingface.co/togethercomputer/GPT-JT-6B-v1)
