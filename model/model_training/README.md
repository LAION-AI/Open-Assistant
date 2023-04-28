# Train using supervised examples

## Requirements

`pip install -e ..` (pyproject.toml resides in the parent directory)

Make sure the oasst_data module is installed

```bash
python -m pip install ../../oasst-data/
```

Run tests: `pytest .`

You might run into a `SystemExit` here for the test
`tests/test_patched_gpt_neox.py::test_flash_attention_patch`. If so just follow
the warning and install `flash_attn`:

```bash
python -m pip install flash_attn
```

Start training SFT model

```bash
python trainer_sft.py --configs galactica-125m
```

If you want to get started with a small amount of test data to begin with, add
the config `webgpt_dataset_only`.

If you kill and want to resume, see the `--resume_from_checkpoint` option.

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
python trainer_sft.py --configs oasst_export_eu galactica-125m
```

Change the `input_file_path` in the `oasst_export_eu` from the
`configs/config.yaml` file to the correct path.

## Training the Reward Model

To experiment with the reward model run:

```bash
python trainer_rm.py --configs defaults_rm oasst-rm-1-pythia-1b
```

Since the model configs are kept quite minimal it is important to overwrite the
other default options (as given by `defaults_rm`) with the model specific ones.

## Training with RL

To train using trlx you first need to install singularity from
https://github.com/sylabs/singularity/blob/main/INSTALL.md.

Assumes access to a server with 8 GPUs.

Then:

```bash
singularity build --sandbox tritonserver-pyt.sif docker://nvcr.io/nvidia/tritonserver:22.08-pyt-python-py3
```

Process a trained RM model to use in a tritonserver

```bash
python to_triton.py --configs pythia_rlhf --triton_mode rm
python to_triton.py --configs pythia_rlhf --triton_mode sft
```

We can know launch the container instance that runs the RM on a specified GPU

```bash
SINGULARITYENV_CUDA_VISIBLE_DEVICES=7 singularity run --nv --bind .triton_models/model_store_rm:/model_store tritonserver-pyt.sif tritonserver --model-repository=/model_store --http-port 8001 --grpc-port 8002 --metrics-port 8003
SINGULARITYENV_CUDA_VISIBLE_DEVICES=6 singularity run --nv --bind .triton_models/model_store_sft:/model_store tritonserver-pyt.sif tritonserver --model-repository=/model_store --http-port 8004 --grpc-port 8005 --metrics-port 8006
```

Finally, we can train using PPO:

```bash
export TRITON_HOST_RM=localhost:8002/<RM_MODEL_NAME>
export TRITON_HOST_REF=localhost:8005/<REF_MODEL_NAME>


CUDA_VISIBLE_DEVICES=0,1,2,3,4,5 OMP_NUM_THREADS=1 accelerate launch --main_process_port 29501 --config_file configs/accelerate_config.yaml --num_processes 6 trainer_rl.py --configs defaults defaults_rlhf pythia_rlhf oasst_export_latin_cyrillic_rlhf
```

Note: `--num_processes` must be equal to the number of GPUs used for training.

## Test your model

You can interactively test your model like this:

```bash
python3 tools/model_cli.py --model_path <saved_path/huggingface>
# For example, if you trained with the default config:
python3 tools/model_cli.py --model_path saved_model
# Add --8bit  if it is an 8bit model
```

Or start a conversation with your bot interactively, mainly for testing context
switch ability

```bash
python3 tools/model_chat.py --model_path <saved_path/huggingface>
# For example, if you trained with the default config:
python3 tools/model_chat.py --model_path saved_model
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

Once you are satisfied with your deepzero config, you can add the --deepspeed
flag at the end to trigger deepspeed. You should typically use the deepspeed
launcher to train

```
deepspeed trainer_sft.py --configs defaults your-model-name --deepspeed
```

### Datasets

Here is an uncomplete overview of datasets for sft:

<!-- prettier-ignore -->
dataset_name                    | train_counts | eval_counts | total_counts
----------------------------------------------------------------

<!-- prettier-ignore -->
joke                            |       301    |      76     |       377
webgpt                          |     14251    |    3563     |     17814
gpt4all                         |    313552    |   78388     |    391940
alpaca                          |     41361    |   10346     |     51707
code_alpaca                     |     16017    |    4004     |     20021
vicuna                          |     46939    |   11735     |     58674
minimath                        |      2304    |     576     |      2880
humaneval_mbpp_codegen_qa       |       472    |     119     |       591
humaneval_mbpp_testgen_qa       |       472    |     119     |       591
grade_school_math_instructions  |      7033    |    1759     |      8792
recipes                         |      3797    |     950     |      4747
cmu_wiki_qa                     |      1288    |     322     |      1610
oa_wiki_qa_bart_10000row        |      8000    |    2000     |     10000
prosocial_dialogue              |    157160    |   26983     |    184143
explain_prosocial               |    360708    |   61248     |    421956
soda                            |    924102    |  231026     |   1155128
oa_leet10k                      |     18728    |    4683     |     23411

This list can be generated with the following command, but beware that this
downloads all available datasets (>100GB):

```bash
python check_dataset_counts.py --datasets all --mode sft
```

One can specify datasets, which can be found in the config corresponding to the
mode the mode (e.g. configs/config.yaml for sft, configs/config_rm.yaml for rm):

```bash
python check_dataset_counts.py --datasets webgpt squad_v2 --mode sft
```

### Troubleshooting

- If training on a VM, you might need to install OpenMPI. Check out
  [this blog post](https://lambdalabs.com/blog/horovod-keras-for-multi-gpu-training#open-mpi-optional)
  by Lambda on how to install OpenMPI on their machines.
- Installing `mpi4py` requires `python-dev`, which can be installed via
  `sudo apt install libpython3.10-dev` (replace `3.10` with whatever Python
  version you're running).

## Results

Experimental results in wandb
[here](https://wandb.ai/sanagnos/supervised-finetuning?workspace=user-sanagnos).

## TODOs

- recreate init in trainer that does not load the ref_model, currently hard
  coded
- same for not loading the self.tokenizer in AccelerateRLTrainer
