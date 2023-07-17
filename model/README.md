<a href="https://github-com.translate.goog/LAION-AI/Open-Assistant/blob/main/model/README.md?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp">![Translate](https://img.shields.io/badge/Translate-blue)</a>

## Reproduction directions

Here are some minimal commands to tun to whole pipeline on the collected data.

**make sure python >= 3.10, otherwise, you would meet the
[[issue]](https://github.com/tiangolo/typer/issues/371#issuecomment-1288987924)**

1. First create the data path location.

```bash
mkdir -p .cache
mkdir -p .saved_models
export DATA_PATH=$PWD/.cache
export MODEL_PATH=$PWD/.saved_models
```

2. Then download the OA message tree JSONL file or declare the HuggingFace
   dataset to use.

Create a new or modify an existing configuration section in the `config.yaml`
(SFT), `config_rm.yaml` (RM) or `config_rl.yaml` (RL) YAML configuration files
located in the `model_training/configs/` directory and specify the OA JSONL data
file or HuggingFace dataset to use.

- To use a local OASST JSONL file (either `.jsonl` or `.jsonl.gz`) specify the
  file name with the `input_file_path` configuration option. Place the file
  either in the `cache_dir` (`DATA_PATH`) or specify an absolute path.

```bash
cp /path/to/<oasst.trees.jsonl> $DATA_PATH
```

Example:

```yaml
my_data_config:
  datasets:
    - oasst_export:
      input_file_path: oasst_export.trees.jsonl.gz
```

- To use a HuggingFace dataset specify the dataset name with the
  `hf_dataset_name` configuration option.

Example:

```yaml
my_data_config:
  datasets:
    - oasst_export:
      hf_dataset_name: OpenAssistant/oasst1
```

_Note_: If both `hf_dataset_name` and `input_file_path` are specified
`input_file_path` will take precedence.

See the
[OpenAssistant/oasst1](https://huggingface.co/datasets/OpenAssistant/oasst1)
dataset card on the HuggingFace hub for more information.

- (TODO) add better parsing of the config files that is consistent for sft, rm
  and rl training.

### SFT Training

3. Start with the SFT training.

```bash
cd model_training
# export shared modules
export PYTHONPATH=$PYTHONPATH:../../oasst-shared

python trainer_sft.py --configs defaults oa_dataset_only pythia --cache_dir $DATA_PATH --output_dir $MODEL_PATH/sft_model

# if you want to use wandb, add
--wandb_entity your_username/team_name
```

To change the model used, i.e. larger pythia version create a new config in
`model_training/configs/config.yaml` or set the flag `--model_name` to
`EleutherAI/pythia-{size}-deduped`. Larger models will probably need to also
adjust the `--learning_rate` and `--per_device_train_batch_size` flags.

4. Get SFT trained model

```bash
# choose a specific checkpoint
export SFT_MODEL=$MODEL_PATH/sft_model/<checkpoint-X>

# or get latest checkpoint
export SFT_MODEL=$MODEL_PATH/sft_model/$(ls -t $MODEL_PATH/sft_model/ | head -n 1)
```

### RM Training

5. Train the reward model

```bash
cd model_training
python trainer_rm.py --configs defaults_rm oasst-rm-1-pythia-1b
```

6. Get RM trained model

```bash
# choose a specific checkpoint
export REWARD_MODEL=$MODEL_PATH/reward_model/<checkpoint-X>

# or get latest checkpoint
export REWARD_MODEL=$MODEL_PATH/reward_model/$(ls -t $MODEL_PATH/reward_model/ | head -n 1)
```

### RL Training

7. Train the RL agent

```bash
cd model_training
python trainer_rl.py --configs defaults_rlhf --cache_dir $DATA_PATH --rank_model $REWARD_MODEL --sft_model $SFT_MODEL --output_dir $MODEL_PATH/rl_model
```

# Message and Token Format

See the `MESSAGE_AND_TOKEN_FORMAT.md` file for information about the pattern we
are using.
