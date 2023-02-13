# Train using supervised examples

## Requirements

`pip install -r requirements.txt`

Start training SFT model

```bash
python trainer_sft.py --configs defaults galactica-125m
```

For `wandb`: update the `entity` argument in `trainer_sft.py`'s call to
`wandb.init` to be your weights and biases username per
[docs](https://docs.wandb.ai/ref/python/init).

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

## Dataset sub-sampling

We can subsample the **training** data by passing either the `fraction` or
`size` argument in the `configs/config.yml` file. Don't forget the additional
colon ":" after the dataset name when doing this.

Example:

```
  datasets:
    - webgpt:
        fraction : 0.05
    - prompt_dialogue:
        size : 500
    - adversarial_qa
    - trivia_qa_nocontext
```

In this example, per epoch we will use:

- A random 5% of `webgpt`;
- A random 500 examples from `prompt_dialogue`;
- All examples from datasets for which we don't specify the `fraction` or `size`
  argument.

In the above example, per epoch we'll use a different 5% from `webgpt` and a
different 500 examples from `prompt_dialogue`.

This works with `torch.distributed`.

## Training only on OA internal data:

To experiment with the Open Assistant data simply run:

```bash
python trainer_sft.py --configs defaults oa_dataset_only galactica-125m
```

Change the `data_path` in the `oa_dataset_only` from the `configs/config.yaml`
file to the correct path.

## Training with RL

To train using trlx try:

```bash
python trainer_rl.py --configs defaults_rlhf
```

## Model

Normally you should be able to add new models in `configs/config.yml`

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
python trainer_sft.py --configs defaults your-model-name
```

However, if the model of your choice doesn't have `pad_token`, `eos_token`,
`sep_token`, you have to update `get_tokenizer` in `utils.py` to use the right
token.

## Deepspeed support

You can edit the configs/zero_config.json and use any stage you wish. The
current config uses zero-stage 3. For more details on how to setup the config
checkout [this page](https://www.deepspeed.ai/tutorials/zero/).

Once you are satisfy with your deepzero config, you can add --deepspeed flag at
the end to trigger deepspeed

```
python trainer_sft.py --configs defaults your-model-name --deepspeed
```

## Results

Experimental results in wandb
[here](https://wandb.ai/sanagnos/supervised-finetuning?workspace=user-sanagnos).

## TODOS

- Decide on a model
- Merge utils etc with reward model
- Casual Modelling for GPT-JT does not leverage the bidirectional mask for the
  prompt? (https://huggingface.co/togethercomputer/GPT-JT-6B-v1)
