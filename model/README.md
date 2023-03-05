## Reproduction directions

Here are some minimal commands to tun to whole pipeline on the collected data.

1. First create the data path location.

```bash
mkdir -p .cache
mkdir -p .saved_models
export DATA_PATH=$PWD/.cache
export MODEL_PATH=$PWD/.saved_models
```

2. Then download the OA data.

```bash
cp /path/to/<oa.jsonl> $DATA_PATH
```

Change the `<oa.jsonl>` file used in the `model_training/configs/config.yaml`,
`model_training/configs/config_rl.yaml` and `reward/instructor/rank_datasets.py`
files.

- (TODO) add better parsing of the config files that is consistent for sft, rm
  and rl training.

### SFT Training

3. Start with the SFT training.

```bash
cd model_training
CUDA_VISIBLE_DEVICES=1 python trainer_sft.py --configs defaults oa_dataset_only pythia --cache_dir $DATA_PATH --output_dir $MODEL_PATH/sft_model
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
cd ../reward/instructor
python trainer.py configs/deberta-v3-base.yml --output_dir $MODEL_PATH/reward_model
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
cd ../../model_training
python trainer_rl.py --configs defaults_rlhf --cache_dir $DATA_PATH --rank_model $REWARD_MODEL --sft_model $SFT_MODEL --output_dir $MODEL_PATH/rl_model
```
