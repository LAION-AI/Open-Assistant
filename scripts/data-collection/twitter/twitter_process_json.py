# This file loops through compressed json tweet data, pre-processes them,
# and then extracts them into more unified parquet files that can be handed
# off for further processing. The main focus is on producing viable replies.

# Initial data exploration seems that there is no guarantee that the original
# tweets are in the archive, so we might need to extract suitable replies
# then get the original tweets separately, and then combine them into a
# suitable thread format that can be used by our instruction model.

# This assumes data downloaded from https://archive.org/details/twitterstream
# and that the internal .tar files are extracted locally.
# They are large files so using something like 7Zip or WinRar might be easier
# than putting all of it in scripts, but it is a possibility.

# I often work in notebooks. If you encounter any issue, please reach out to let me know.

import bz2
import gzip
import json
import pickle
from pathlib import Path

import numpy as np
import polars as pl
from tqdm import tqdm

# TODO: OPTIONAL - Put the Untar process in a script instead of doing that part externally. Twitterstream archives are .tar with folders and json.gz files inside.
# TODO: Set up list of important hashtags & keywords. This might have to be done after we get the original tweets in a separate file.
# TODO: Process data and filter based on hashtags & keywords

# Sets up paths
# TODO: Source paths from env file
path_string = "PUT THE PATH HERE TO WHERE YOU DOWNLOADED AND EXTRACTED THE ARCHIVE .TAR"
folder_path = Path(path_string)
file_list_pkl = folder_path / "file_list.pkl"
processed_file_list_pkl = folder_path / "processed_file_list.pkl"

# For the processed folder to save inside, we can create the directory if it doesn't exist
processed_folder_path = folder_path / "processed"
processed_folder_path.mkdir(parents=True, exist_ok=True)

# Set max buffer to store temporary dataframes for processing
# Change this depending on the memory of your computer
processed_max_buffer = 5000

# Set up list of wanted column names.
# Note: User columns are prefixed with user_
wanted_cols = [
    "timestamp_ms",
    "id",
    "text",
    "truncated",
    "in_reply_to_status_id",
    "in_reply_to_user_id",
    "is_quote_status",
    "quote_count",
    "reply_count",
    "retweet_count",
    "favorite_count",
    "filter_level",
    "lang",
    "possibly_sensitive",
    "hashtags",
    "user_id",
    "user_verified",
    "user_followers_count",
    "user_statuses_count",
]


def main(file_list_pkl, folder_path, processed_max_buffer):
    """
    Runs the main processing script to get files, loop through them, and process them.
    Outputs larger json.gz files made by concat the pre-filtered dataframes from
    the original json.gz files.
    """

    file_list = get_file_paths(file_list_pkl, folder_path)

    process_json(file_list, processed_max_buffer)

    print("Done")


def get_file_paths(file_list_pkl, folder_path):
    """
    Gets the file paths by recursively checking the folder structure.
    # Based on code from stackoverflow https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
    """
    try:
        allpaths = pickle.load(open(file_list_pkl, "rb"))
    except (OSError, IOError) as e:
        print(e)
        allpaths = sorted(list(folder_path.rglob("*.[gz bz2]*")))
        pickle.dump(allpaths, open(file_list_pkl, "wb"))
    print("Got file paths.")
    return allpaths


def get_processed_list(processed_file_list_pkl):
    # Gets processed file list if stored, if not, creates it.
    try:
        processed_list = pickle.load(open(processed_file_list_pkl, "rb"))
    except (OSError, IOError) as e:
        print(e)
        processed_list = []
        pickle.dump(processed_list, open(processed_file_list_pkl, "wb"))
    return processed_list


def modify_dict_cols(j_dict):
    # Extracting some nested json
    j_dict["user_id"] = np.int64(j_dict["user"]["id"])
    j_dict["user_followers_count"] = np.int64(j_dict["user"]["followers_count"])
    j_dict["user_statuses_count"] = np.int64(j_dict["user"]["statuses_count"])

    # Get hashtags as a list of strings
    j_dict["hashtags"] = [h["text"] for h in j_dict["entities"]["hashtags"]]

    j_dict["id"] = np.int64(j_dict["id"])

    try:
        j_dict["in_reply_to_status_id"] = np.int64(j_dict["in_reply_to_status_id"])
    except Exception as e:
        print(e)
        j_dict["in_reply_to_status_id"] = j_dict["in_reply_to_status_id"]

    try:
        j_dict["in_reply_to_user_id"] = np.int64(j_dict["in_reply_to_user_id"])
    except Exception as e:
        print(e)
        j_dict["in_reply_to_user_id"] = j_dict["in_reply_to_user_id"]

    # Make sure relevant columns are available or none.
    for key in wanted_cols:
        if key not in j_dict:
            j_dict[key] = None

    # Ordering keys and taking wanted columns
    j_dict = {key: j_dict[key] for key in wanted_cols}

    return j_dict


def process_single_file(f, processed_list):
    j_dict_list = []
    if f not in processed_list:
        # Check for compression type
        if f.suffix == ".bz2":
            with bz2.BZ2File(f) as file:
                for line in file:
                    # Load JSON
                    j_dict = json.loads(line)
                    # Check if user key exists
                    if "delete" not in j_dict:
                        if j_dict["truncated"] is False:
                            j_dict = modify_dict_cols(j_dict)

                            j_dict_list.append(j_dict)

        else:
            with gzip.open(f, "r") as file:
                for line in file:
                    # Load JSON
                    j_dict = json.loads(line)
                    # Check if user key exists
                    if "delete" not in j_dict:
                        if j_dict["truncated"] is False:
                            j_dict = modify_dict_cols(j_dict)

                            j_dict_list.append(j_dict)

        return j_dict_list


def process_json(file_list, processed_max_buffer):
    """
    Loops through file list and loads the compressed
    json into a list of dicts after some pre-processing.

    Makes sure dicts are ordered in a specific
    way to make sure polars can read them.
    """

    # Gets processed file list if stored, if not, creates it.
    processed_list = get_processed_list(processed_file_list_pkl)

    j_list = []
    temp_processed_files = []

    for i, f in enumerate(tqdm(file_list)):
        j_dict_list = process_single_file(f, processed_list)

        j_list.extend(j_dict_list)

        temp_processed_files.append(f)

        if len(temp_processed_files) == processed_max_buffer:
            # If we reach our buffer,
            # combine into polars dataframe
            # and write to parquet as
            # a checkpoint
            processed_file_name = f"processed_json_{i}.parquet"
            processed_file_path = processed_folder_path / processed_file_name

            pl.DataFrame(j_list, columns=wanted_cols).write_parquet(processed_file_path)

            # Make note of which files have been processed
            processed_list.extend(temp_processed_files)
            pickle.dump(processed_list, open(processed_file_list_pkl, "wb"))

            # Reset buffer lists
            j_list = []
            temp_processed_files = []

    # Process remaining files
    processed_file_name = f"processed_json_{i}.parquet"
    processed_file_path = processed_folder_path / processed_file_name
    pl.from_dicts(j_dict_list).write_parquet(processed_file_path)
    processed_list.extend(temp_processed_files)
    pickle.dump(processed_list, open(processed_file_list_pkl, "wb"))
    j_dict_list = []
    temp_processed_files = []

    print("Processing completed")


if __name__ == "__main__":
    main(file_list_pkl, folder_path, processed_max_buffer)
