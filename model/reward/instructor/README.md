# Sections to train Reward Model (RM)

Trainer code based on huggingface. Compatible with deepspeed or accelerate

## Requirements

`pip install .`

Write or inherit a `configs/<config-name>.yml` file to store training
configuration details.

> The configuration file must have _at least_ all the keys present in
> [`configs/dummy.yml`](configs/dummy.yml)

Run training procedure

```bash
python trainer.py configs/<config-name>.yml
```

Additional axis labeling, this outputs a 4 summary quality evaluation metrics
(score are normalized to 0-1 )

```bash
python summary_quality_trainer.py configs/test-bloomz-560m-quality.yml
```

The four summary are :

- overall

- accuracy

- coverage

- coherence

## Dataset

For now we only supports webgpt and summary dataset from OpenAI. Once
open-asisstant dataset are available it will be added here.

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
