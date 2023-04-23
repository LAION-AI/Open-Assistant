import glob
import re

from pyarrow.parquet import ParquetDataset


def rows(topic):
    dataset = ParquetDataset(f"parquet/{topic}.parquet")
    return sum(p.count_rows() for p in dataset.fragments)


for f in sorted(glob.glob("parquet/*.parquet")):
    topic = re.match(r".*\/(.*?)\.parquet", f)[1]
    num = rows(topic)
    print(f"- {topic}: {int(num):,}")
