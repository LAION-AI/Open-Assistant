import torch
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    EvalPrediction,
    DataCollator,
    Trainer,
    TrainingArguments)


LABEL2ID = {
    "__casual__": "__casual__",
    "__needs_caution__": "__needs_caution__",
    "__needs_intervention__": "__needs_intervention__",
    "__probably_needs_caution__": "__probably_needs_caution__",
    "__possibly_needs_caution__": "__possibly_needs_caution__",
}

SPECIAL_TOKENS = {"context_token":"<ctx>","sep_token":"<sep>","label_token":"<cls>","rot_token":"<rot>"}
MAX_LEN = 256
EPOCHS = 1
MODEL = "t5-base"
BATCH_SIZE = 8
DATASET_NAME = "allenai/prosocial-dialog"
FP16 = False
ROOT_DIR = ""



if __name__ == "__main__":

    if not os.path.exists(ROOT_DIR):
        os.mkdir(ROOT_DIR)
    
    model = T5ForConditionalGeneration.from_pretrained(MODEL)
    tokenizer = T5Tokenizer.from_pretrained(MODEL,padding_side="right",truncation_side="right",model_max_length=512)
    add_special_tokens(SPECIAL_TOKENS,tokenizer,model)

    dataset = load_dataset(DATASET_NAME)
    train_dataset = SafetyDataset(dataset,split=["train","validation"],tokenizer=tokenizer,max_len=MAX_LEN)
    valid_dataset = SafetyDataset(dataset,split="test",tokenizer=tokenizer,max_len=MAX_LEN)
    
    training_args = TrainingArguments(output_dir=ROOT_DIR, 
                                  per_device_train_batch_size=BATCH_SIZE, 
                                  per_device_eval_batch_size=BATCH_SIZE,
                                  num_train_epochs=EPOCHS,
                                  logging_steps=100,
                                  evaluation_strategy="steps",
                                  eval_steps=1000,
                                  save_steps=5000,
                                  push_to_hub=False,
                                  fp16=FP16)


    # Initialize our Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=T2TDataCollator()
    )

    # Training
    trainer.train()

    #trainer.push_to_hub("")

    #trainer.save_model(os.path.join(ROOT_DIR,"safety-model"))
    tokenizer.save_vocabulary(os.path.join(ROOT_DIR,"safety-tokenizer"))