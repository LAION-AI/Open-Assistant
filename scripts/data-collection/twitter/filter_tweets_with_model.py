import json
from datetime import datetime

from tqdm import tqdm
from transformers import pipeline

tweet_threads_file = "twitter-conv-trees.jsonl"

tweets = []
with open(tweet_threads_file, "r") as f:
    for line in f:
        json_object = json.loads(line)
        tweets.append(json_object)

classifier = pipeline("text-classification", model="jmete/tweet_instruct_detect")

# Create exportable conv thread.
instruct_threads = []

for i in tqdm(tweets):
    pred = classifier(i["root"]["text"])
    if pred[0]["label"] == "instruction":
        i["root"]["metadata"]["instruction_score"] = pred[0]["score"]
        instruct_threads.append(i)

print(f"Found {len(instruct_threads)} Instructions")

the_date = datetime.today().strftime("%Y-%m-%d")

# export instruct_threads to jsonl
with open(f"tweet-conv-trees-instructions-{the_date}.jsonl", "w") as f:
    for item in instruct_threads:
        f.write(json.dumps(item) + "\n")
