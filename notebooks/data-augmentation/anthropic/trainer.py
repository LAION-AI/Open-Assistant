import numpy as np
from datasets import load_dataset
from sklearn.metrics import f1_score
from torch.utils.data import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

MAXLEN = 128
BATCH_SIZE = 128
MODEL = "roberta-base"
LABEL2ID = {
    "__casual__": 0,
    "__needs_caution__": 1,
    "__needs_intervention__": 2,
    "__probably_needs_caution__": 3,
    "__possibly_needs_caution__": 4,
}


class ProSocialDataset(Dataset):
    def __init__(self, split):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.sep_token = self.tokenizer.sep_token
        self.dataset = load_dataset("allenai/prosocial-dialog", split=split)
        self.label2id = LABEL2ID
        self.id2label = {v: k for k, v in LABEL2ID.items()}

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        context = self.dataset[idx]
        idx_start = idx
        end = self.dataset[max(0, idx_start - 1)]["episode_done"]
        while (not end) and (idx_start > 0):
            end = self.dataset[max(0, idx_start - 2)]["episode_done"]
            idx_start -= 1
        idx_start = max(0, idx_start)

        prev_context = [f'{self.dataset[i]["context"]}' for i in range(idx_start, idx)]
        rots = self.dataset[idx]["rots"]
        context = (
            f'{self.dataset[idx]["context"]}' + self.sep_token + "".join(prev_context) + self.sep_token + "".join(rots)
        )

        encoding = self.tokenizer(
            context, max_length=MAXLEN, add_special_tokens=True, truncation=True, padding="max_length"
        )

        encoding["labels"] = self.label2id[self.dataset[idx]["safety_label"]]

        return encoding


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {"f1": f1_score(labels, predictions, average="micro")}


if __name__ == "__main__":
    train_dataset = ProSocialDataset("train")
    eval_dataset = ProSocialDataset("validation")

    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(LABEL2ID))

    training_args = TrainingArguments(
        output_dir="test_trainer",
        overwrite_output_dir=True,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=3e-5,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        num_train_epochs=5,
        load_best_model_at_end=True,
        save_strategy="epoch",
    )

    trainer_bert = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    trainer_bert.train()
