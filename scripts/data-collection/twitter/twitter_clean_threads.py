# This file takes in an input the pkl file
# that was exported from twitter_scrape_threads
# It cleans up that dict into a list of cleaned
# strings and removes some empty or very short threads.

import json
import pickle
import re

from tqdm import tqdm

# SET UP MAIN VARIABLES
pickle_dict_path = "processed_threads.pkl"
output_save = "cleaned_threads.jsonl"

# HELPER FUNCTIONS


def main(pickle_dict_path, output_save):
    """
    Runs main script to load pickle of threads dict,
    cleans them and then saves the result to jsonl output.
    """

    # Load pickle
    print("Loading dict from pickle...")
    with open(pickle_dict_path, "rb") as f:
        threads = pickle.load(f)

    print("Cleaning threads...")
    cleaned_threads = clean_threads(threads)

    print(f"Cleaned threads resulting in {len(cleaned_threads)} threads.")

    print("Saving file to jsonl...")
    # Save to jsonl file
    with open(output_save, "w") as file:
        for thread in cleaned_threads:
            flines = json.dumps(thread) + "\n"
            file.write(flines)

    print("Done. Saved jsonl file to specified directory.")


def clean_thread(thread):
    """
    Takes in a thread list of tweets,
    and cleans them into a single
    long string of text. Removes
    twitter usernames, newline characters,
    and formats with single space after period.
    """
    cleaned_stack = ""
    # Regex for twitter usernames and newlines
    cleaned = [re.sub(r"(@\w+|\n)", "", tweet) for tweet in thread]

    # Combined cleaned strings into 1 string.
    for c in cleaned:
        cleaned_stack += c

    # Replace double-space with single-space after period.
    cleaned_stack = cleaned_stack.replace(".  ", ". ")

    return cleaned_stack


def clean_threads(threads):
    """
    Loops through dict of threads,
    and cleans them up.

    Returns list of strings
    representing each thread as
    one long cleaned string.
    """

    cleaned_threads = []

    for tweet in tqdm(threads):
        # Remove empty lists
        if len(threads[tweet]) > 0:
            c_t = clean_thread(threads[tweet])
            # Only save threads longer than 50 characters.
            # Helps remove some spam or image threads.
            if len(c_t) > 50:
                cleaned_threads.append(c_t)

    return cleaned_threads


if __name__ == "__main__":
    main(pickle_dict_path=pickle_dict_path, output_save=output_save)
