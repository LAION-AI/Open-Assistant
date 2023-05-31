source /home/ubuntu/venv/bin/activate

cd /home/ubuntu/Open-Assistant
export TRANSFORMERS_CACHE=/home/ubuntu/transformers_cache

cd /home/ubuntu/Open-Assistant/model/model_training
deepspeed --include=localhost:0,1 --master_port 61500 /home/ubuntu/Open-Assistant/model/model_training/trainer_sft.py --configs defaults oasst-top1 falcon-7b-lora --cache_dir /home/ubuntu/Open-Assistant/data_cache --output_dir /home/ubuntu/Open-Assistant/output_dir 2>&1 --deepspeed | tee debug_falcon.txt
