import logging
import os

import pandas as pd
import praw
import prawcore
import utils
from tqdm import tqdm

logger = logging.getLogger(__name__)


def init_praw_reddit(client_id: str | None = None, client_secret: str | None = None, user_agent: str | None = None):
    # setup praw
    CLIENT_ID = client_id if client_id else os.environ.get("CLIENT_ID")
    CLIENT_SECRET = client_secret if client_secret else os.environ.get("CLIENT_SECRET")
    USER_AGENT = user_agent if user_agent else os.environ.get("USER_AGENT")

    # the client that communicates with reddit.
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
    )
    return reddit


def scrap_subreddit(subreddit: str, reddit) -> pd.DataFrame | None:
    """
    Scrap "hot", "top", "rising" given a subreddit and return
    dedupped DataFrame.
    """
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
            items.append(item)
        dfs.append(pd.DataFrame(items))

    df = pd.concat(dfs)
    return df.drop_duplicates(subset=["post_id"])


def get_comments(post_ids: list, reddit: praw.Reddit):
    """
    Get comments for the give list of post_ids.
    """
    NUM_COMMENTS = 5
    items = []
    for i, post_id in enumerate(tqdm(post_ids)):
        try:
            item = {"post_id": post_id}
            post = reddit.submission(post_id)
            for j, c in enumerate(post.comments[:NUM_COMMENTS]):
                item[f"C{j+1}"] = c.body
            items.append(item)
        except Exception as e:  # noqa
            logger.error(f"Error getting comments for {post_id}: {e}")
        if not (i + 1) % 100:
            pd.DataFrame(items).to_csv(f"comments_cache/num_{i}.csv", index=False)
            print(f"[epoch-{i}]: Saved!")
    pd.DataFrame(items).to_csv("df_with_comments.csv", index=False)
