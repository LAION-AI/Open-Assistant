import json
from pathlib import Path

import polars as pl
from tqdm import tqdm

# Sets up paths
# TODO: Source paths from env file
path_string = "PUT THE PATH HERE TO WHERE YOU STORED THE PARQUET FILES"
folder_path = Path(path_string)
processed_folder_path = folder_path / "processed"
output_path = folder_path / "twitter-conv-trees.jsonl"

# Get parq files
parq_files = sorted(processed_folder_path.rglob("*.parquet"))

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

# Load parqs into list. Using Polars for performance reasons.
df_list = []
for p in parq_files:
    df_list.append(pl.read_parquet(p, columns=wanted_cols))

# Create major dataframe.
# This can be done incrementally if RAM is constrained by modifying the above code.
p_df = pl.concat(df_list)

# Clean up the reference just in case to help with memory if needed.
del df_list

# Get tweets that are replies to other tweets
p_df_replies_only = p_df.filter(pl.col("in_reply_to_status_id").is_null().is_not())

# Group by replied to status id to see the most replied to statuses. This can take some time.
p_df_group_reply_to_status = p_df_replies_only.groupby("in_reply_to_status_id").count().sort("count", reverse=True)

# Save output of grouping the top replied to statuses
group_reply_parq = folder_path / "group_reply_parq.parquet"
p_df_group_reply_to_status.write_parquet(group_reply_parq)

# Join the main dataframe with the top replies to find tweets that have replies.
p_join = p_df.join(p_df_group_reply_to_status, left_on="id", right_on="in_reply_to_status_id", how="inner")

# Save output of tweets that have replies
tweets_that_have_replies_path = folder_path / "tweets_that_have_replies.parquet"
p_join.write_parquet(tweets_that_have_replies_path)

# Save output of tweets that are replies to other tweets
tweets_that_are_replies_path = folder_path / "tweets_that_are_replies.parquet"
p_df_replies_only.write_parquet(tweets_that_are_replies_path)

# Filter the tweets that have replies to ones that aren't replies to others.
# Also filter for only english for now.
# This gives the root tweets that have replies but are the start of a conversation.
origin_tweets = p_join.filter((pl.col("in_reply_to_status_id").is_null()) & (pl.col("lang") == "en"))


# Helper functions and classes below for the next steps


def role_decide(user_id, prompt_user):
    if user_id == prompt_user:
        return "prompter"
    else:
        return "assistant"


class ConversationTreeNode:
    def __init__(self, tweet_id, prompt_user, from_df, children_df, metadata=None):
        if metadata:
            self.metadata = metadata
        else:
            self.metadata = from_df.filter(pl.col("id") == tweet_id).to_dicts()[0]

        self.metadata["prompt_user"] = prompt_user
        self.role = role_decide(self.metadata["user_id"], prompt_user)
        self.children = None
        self.text = self.metadata["text"]
        del self.metadata["text"]
        self.get_children(tweet_id=tweet_id, children_df=children_df)

    def get_children(self, tweet_id, children_df):
        children_dicts = children_df.filter(pl.col("in_reply_to_status_id") == tweet_id).to_dicts()
        if len(children_dicts) > 0:
            children = [
                ConversationTreeNode(
                    tweet_id=c["id"],
                    prompt_user=self.metadata["prompt_user"],
                    from_df=children_df,
                    children_df=children_df,
                    metadata=c,
                )
                for c in children_dicts
            ]
            self.children = children


class ConversationTree:
    def __init__(self, tweet_id, prompt_user, from_df, children_df, r_metadata=None):
        self.root = ConversationTreeNode(
            tweet_id=tweet_id, prompt_user=prompt_user, from_df=from_df, children_df=children_df, metadata=r_metadata
        )
        self.metadata = None


# Create conversation trees
conv_tree_list = [
    ConversationTree(
        tweet_id=r["id"], prompt_user=r["user_id"], from_df=origin_tweets, children_df=p_df_replies_only, r_metadata=r
    )
    for r in tqdm(origin_tweets.to_dicts())
]

# Write conversation trees to jsonl file.
# Might need to clean up the last newline.
with open(output_path, "w") as output:
    for t in tqdm(conv_tree_list):
        json.dump(obj=t, fp=output, default=lambda x: x.__dict__)
        output.write("\n")
