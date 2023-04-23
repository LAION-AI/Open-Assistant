#!/usr/bin/env python3
#
# Simple script to download StackExchange archive XML files with posts (threaded version)
#
# Note: you probably want to download stackoverflow.com-Posts.7z manually, as it is 18GB
# and takes a days to download otherwise. You can try using the torrent:
#
# webtorrent https://archive.org/download/stackexchange/stackexchange_archive.torrent --select 658
#

import concurrent.futures
import os
import re

import requests
from bs4 import BeautifulSoup as bs

BASE_URL = "https://ia600107.us.archive.org/view_archive.php?archive=/27/items/stackexchange/{0}&file=Posts.xml"
DOWNLOAD_DIR = "xml/"
NUM_PARALLEL = 20
RE_IGNORE = r"_meta|stackoverflow\.com\-"


def get_all_filenames():
    """
    Retrieve all urls from stackexchange archive.
    This needs quite some mangling because of special cases (i.e. stackoverflow is not in one 7z archive).
    Ignore meta files.
    """
    response = requests.get("https://archive.org/download/stackexchange")
    if response.ok:
        soup = bs(response.content, "html.parser")
        table = soup.find("table")
        link_tags = table.find_all("a")
        urls = {"stackoverflow": "https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z"}
        for link in link_tags:
            url = link["href"]
            name = url.split(".stackexchange")[0].replace(".", "_").replace("-", "_")
            name = name.replace("_com_7z", "")
            if url.endswith("7z") and not re.search(RE_IGNORE, url):
                urls[name] = BASE_URL.format(url)
        return urls


def download_url(dataset_name: str, url: str):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    cache_path = os.path.join(DOWNLOAD_DIR, dataset_name + ".xml")
    if os.path.exists(cache_path):
        print("Using cached: ", cache_path)
        return cache_path
    else:
        print("Downloading xml: ", dataset_name)
        response = requests.get(url)
        print("Finished downloading: ", dataset_name)
        with open(cache_path, "wb") as f:
            f.write(response.content)
        return cache_path


def download_all():
    urls = get_all_filenames()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PARALLEL) as executor:
        futures = [executor.submit(download_url, dataset, url) for dataset, url in urls.items()]

    # Wait for all downloads to complete
    concurrent.futures.wait(futures)
    print("All downloads complete, except for the large stackoverflow XML file")
    print("Use torrent to download this one much quicker, then uncompress the 7z file")
    print("and move the extracted stackoverflow.com-Posts.xml to xml/stackoverflow.xml")
    print("webtorrent https://archive.org/download/stackexchange/stackexchange_archive.torrent --select 658")


if __name__ == "__main__":
    download_all()
