from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, TypeVar

import pyarrow as pa
import pyarrow.parquet as pq


def stream_to_parquet(path: Path, tables: Iterable[pa.Table]) -> None:
    try:
        first = next(tables)
    except StopIteration:
        return
    schema = first.schema
    with pq.ParquetWriter(path, schema) as writer:
        writer.write_table(first)
        for table in tables:
            table = table.cast(schema)  # enforce schema
            writer.write_table(table)


def stream_from_parquet(path: Path) -> Iterable[pa.Table]:
    reader = pq.ParquetFile(path)
    for batch in reader.iter_batches():
        yield pa.Table.from_batches([batch])


def stream_from_parquets(paths: Iterable[Path]) -> Iterable[pa.Table]:
    for path in paths:
        yield from stream_from_parquet(path)


T = TypeVar("T")


def coalesce(items: Iterable[T], max_size: int, sizer: Callable[[T], int] = len) -> Iterable[list[T]]:
    batch = []
    current_size = 0
    for item in items:
        this_size = sizer(item)
        if current_size + this_size > max_size:
            yield batch
            batch = []
            current_size = 0
        batch.append(item)
        current_size += this_size
    if batch:
        yield batch


def coalesce_parquets(paths: Iterable[Path], outpath: Path, max_size: int = 2**20) -> None:
    tables = stream_from_parquets(paths)
    # Instead of coalescing using number of rows as your metric, you could
    # use pa.Table.nbytes or something.
    # table_groups = coalesce(tables, max_size, sizer=lambda t: t.nbytes)
    table_groups = coalesce(tables, max_size)
    coalesced_tables = (pa.concat_tables(group) for group in table_groups)
    stream_to_parquet(outpath, coalesced_tables)


def merge_parquet_dir(path: str, outpath: Path) -> None:
    paths = Path(path).glob("*.parquet")
    coalesce_parquets(paths, outpath)
