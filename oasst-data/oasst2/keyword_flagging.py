import argparse
import csv
import glob
import json
import re

banned_words = {
    "卐",
    "mein führer",
    "sieg heil",
    "heil hitler" "child porn",
    "childporn",
    "loli",
    "hentai",
    "pedophile",
    "nigger",
    "nigga",
    "faggot",
    "tranny",
    "faggy",
    "пидор",
    "хуесос",
    "хуйло",
    "хохол",
    "хохлы",
    "русня",
}


def parse_args():
    parser = argparse.ArgumentParser(description="filter_dataset")
    parser.add_argument(
        "input_file_name",
        type=str,
        help="path to input .jsonl or .jsonl.gz input file",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="dir to output",
    )
    args = parser.parse_args()
    return args


def contains_banned_word(text):
    pattern = r"\b(?:" + "|".join(re.escape(word) for word in banned_words) + r")\b"
    regex = re.compile(pattern, re.IGNORECASE)
    return bool(regex.search(text))


def process_message(msg, writers):
    text = msg.get("text", "")
    if contains_banned_word(text):
        writers["hate_speech_ban_words"].writerow([msg["message_id"], text])
    if "labels" in msg:
        for label in ["hate_speech", "toxicity", "pii", "not_appropriate", "violence"]:
            if label in msg["labels"] and msg["labels"][label]["value"] > 0.85:
                writers[label].writerow([msg["message_id"], text])
    if len(text) < 10:
        writers["junk_by_len"].writerow([msg["message_id"], text])
    if "replies" in msg:
        for reply in msg["replies"]:
            process_message(reply, writers)


def process_jsonl_file(file, writers):
    print(f"Processing file: {file}")
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip())
            if "prompt" in data:
                process_message(data["prompt"], writers)


if __name__ == "__main__":
    args = parse_args()
    files = glob.glob(args.input_file_name)
    if not files:
        print("No files found")
    for file in files:
        with open(
            f"{args.output_dir}/hate_speech_labelled.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file1, open(
            f"{args.output_dir}/hate_speech_ban_words.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file2, open(
            f"{args.output_dir}/junk_len.csv", "w", newline="", encoding="utf-8"
        ) as file3, open(
            f"{args.output_dir}/toxicity_labelled.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file4, open(
            f"{args.output_dir}/pii_labelled.csv", "w", newline="", encoding="utf-8"
        ) as file5, open(
            f"{args.output_dir}/not_appropriate_labelled.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file6, open(
            f"{args.output_dir}/violence_labelled.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file7:
            writers = {
                "hate_speech": csv.writer(file1),
                "hate_speech_ban_words": csv.writer(file2),
                "junk_by_len": csv.writer(file3),
                "toxicity": csv.writer(file4),
                "pii": csv.writer(file5),
                "not_appropriate": csv.writer(file6),
                "violence": csv.writer(file7),
            }
            process_jsonl_file(file, writers)
