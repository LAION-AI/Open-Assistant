import os
import posixpath
from urllib.parse import urljoin, urlparse

from datasets import load_dataset_builder

ds_mapping = {
    # name: repo_id
    "dolly15k": "OllieStanley/oa_dolly_15k",
    "webgpt": "openai/webgpt_comparisons",
    "soda": "allenai/soda",
    "soda_dialogue": "emozilla/soda_synthetic_dialogue",
}


def is_remote_url(url_or_filename: str) -> bool:
    parsed = urlparse(url_or_filename)
    return parsed.scheme in ("http", "https", "s3", "gs", "hdfs", "ftp")


def check_if_dataset_is_local(name: str, cache_dir: str = ".cache") -> bool:
    # todo: maybe we can speed this up if
    # we just copy the correct stuff and don't invoke the whole dataset_builder
    if repo_id := ds_mapping.get(name):
        builder = load_dataset_builder(path=repo_id, cache_dir=cache_dir)
        is_local = not is_remote_url(builder._cache_dir_root)
        path_join = os.path.join if is_local else posixpath.join
        joined_path = path_join(
            builder._cache_dir_root, builder._relative_data_dir(with_version=True, is_local=is_local)
        )
        return os.path.exists(joined_path)
    else:
        return False
