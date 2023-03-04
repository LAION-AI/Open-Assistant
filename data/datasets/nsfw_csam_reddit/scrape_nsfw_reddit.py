import logging
import os

import pandas as pd
import praw
import prawcore
import utils
from tqdm import tqdm

logger = logging.getLogger(__name__)

# setup praw
CLIENT_ID = "ON-Jk8euNrhTBNKaQYyP9Q"
CLIENT_SECRET = "Lrgf4vzTW3K4VMBpNJF9O49u-EJ8Sg"
USER_AGENT = "web:in.jjmachan.scrapper:v0.1.0 (by u/jjmachan)"

# the client that communicates with reddit.
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

subs = [
    "Sexpolls",
    "sexpositions",
    "Sexconfessional",
    "penissize",
    "masturbation",
    "AskRedditNSFW",
    "sexstories",
    "SexFantasies",
    "sexconfession",
    "askwoman_aboutsex",
    "sextips",
    "sexualhealth",
    "SexPositive",
    "DirtyConfession",
    "Puberty",
    "NSFWIAMA",
    "sexover30",
    "SexToys",
    "sexquestions",
    "deepvaginaproblems",
    "kegels",
    "sexeducation",
    "ColoredLang",
    "masterbationstories",
    "RedditAfterDark",
    "Threesome_advice",
]


def scrape_subreddit(subreddit: str) -> pd.DataFrame | None:
    # NUM_COMMENTS = 5
    items = []
    dfs = []

    sub = reddit.subreddit(subreddit)
    try:
        sub.id
    except prawcore.exceptions.ResponseException as e:
        logger.error(f"Error getting {subreddit}: {e}")
        return
    ordering = (sub.hot(limit=1000), sub.top(limit=1000), sub.rising(limit=1000))
    for order in ordering:
        for post in tqdm(order, leave=False):
            item = {
                "title": post.title,
                "subreddit": sub.display_name,
                "post_id": post.id,
                "score": post.score,
                "link_flair_text": post.link_flair_text,
                "is_self": post.is_self,
                "over_18": post.over_18,
                "upvote_ratio": post.upvote_ratio,
                "is_question": utils.is_question(post.title),
            }
            # for i, c in enumerate(post.comments[:NUM_COMMENTS]):
            #     item[f"C{i+1}"] = c.body
            items.append(item)
        dfs.append(pd.DataFrame(items))

    df = pd.concat(dfs)
    return df.drop_duplicates(subset=["post_id"])


def add_comments(df_filepath: os.PathLike) -> pd.DataFrame:
    ...


if __name__ == "__main__":
    for sub in tqdm(subs):
        try:
            df = scrape_subreddit(sub)
            if df is not None:
                file_name = f"dataframes/{sub}.csv"
                df.to_csv(file_name, index=False)
                print("subreddit saved to: ", file_name)
        except Exception as e:
            logger.error(f"Error scraping {sub}: {e}")
