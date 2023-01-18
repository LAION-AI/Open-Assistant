from custom_datasets.prompt_dialogue import PromptGeneratedDataset
from custom_datasets.qa_datasets import SODA, JokeExplaination, QADataset, WebGPT
from custom_datasets.summarization import SummarizationDataset
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset

QA_DATASETS = ["squad_v2", "adversarial_qa", "trivia_qa_context", "trivia_qa_nocontext", "gsm8k"]
SUMMARIZATION_DATASETS = ["xsum", "cnn_dailymail", "samsum", "multi_news", "scitldr", "billsum"]


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(conf, dataset_name):
    dataset_name = dataset_name.lower()

    if dataset_name in QA_DATASETS:
        train = QADataset(dataset_name, conf.cache_dir, "train")
        val_name = "validation" if dataset_name not in ["gsm8k"] else "test"
        eval = QADataset(dataset_name, conf.cache_dir, val_name)

    elif dataset_name in SUMMARIZATION_DATASETS:
        train = SummarizationDataset(dataset_name, conf.cache_dir, "train")
        val_name = "validation" if dataset_name not in ["billsum"] else "test"
        eval = SummarizationDataset(dataset_name, conf.cache_dir, val_name)
    elif dataset_name == "webgpt":
        dataset = WebGPT()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "prompt_dialogue":
        dataset = PromptGeneratedDataset(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "soda":
        dataset = SODA(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.1)
    elif dataset_name == "joke":
        dataset = JokeExplaination(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.2)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    return train, eval
