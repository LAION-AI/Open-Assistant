from datasets import Dataset

ds = Dataset.from_parquet("dataset.parquet")
ds.push_to_hub("wangrui6/Zhihu-KOL")
