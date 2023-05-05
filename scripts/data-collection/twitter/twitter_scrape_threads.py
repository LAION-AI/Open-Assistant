# This file scrapes tweets using snscrape
# We are searching for twitter threads by finding tweets
# where people unroll the content. We can then
# scrape those urls for the thread content.

# This script will save pkl files for the urls
# and a dictionary of url: thread content
# as a list of strings.

# This dict should then be run through
# the accompanying twitter_clean_threads script
# which will remove duplicates and clean up
# the content into large strings.

import itertools
import pickle
import time

import pandas as pd
import requests
import snscrape.modules.twitter as sntwitter
from bs4 import BeautifulSoup
from tqdm import tqdm

# SET UP MAIN VARIABLES
search_string = "from:threadreaderapp"
num_tweets = 100000  # Only ~50-60k in practice
processed_file_urls_pkl = "thread_url_list.pkl"
processed_file_list_pkl = "processed_threads.pkl"
process_buffer = 100

# HELPER FUNCTIONS


def main(search_string, num_tweets, processed_file_urls_pkl, processed_file_list_pkl, process_buffer=100):
    """
    Runs main script to scrape thread URLs, content,
    and saves to pickle files.
    """

    # Get URLs
    print("Scraping tweets and getting URLs...")
    url_list = get_thread_urls(
        search_string=search_string, num_tweets=num_tweets, scrape=True, load_pkl_path=processed_file_urls_pkl
    )
    print("Finished scraping {len(url_list)} URLs. Be aware some of these may be duplicates or empty.")

    # Scrape Threads
    print("Scraping URLs for thread content...")
    tweet_threads = get_threads(
        url_list=url_list, processed_file_path=processed_file_list_pkl, process_buffer=process_buffer
    )
    print(f"Finished scraping {len(tweet_threads)} tweet_threads.")

    print("Done. Files saved to local directory.")


def get_processed_list(processed_file_list_pkl, need_dict=False):
    """
    Gets processed file list if stored, if not, creates it.
    Helps resume operation if scrape fails.
    """

    try:
        processed_list = pickle.load(open(processed_file_list_pkl, "rb"))
    except (OSError, IOError) as e:
        print(e)
        if need_dict is True:
            processed_list = {}
        else:
            processed_list = []
        pickle.dump(processed_list, open(processed_file_list_pkl, "wb"))
    return processed_list


def get_thread_urls(search_string, num_tweets, scrape=True, load_pkl_path=None):
    """
    Uses snscrape to search for a specified
    number of tweets and returns the list
    of unrolled thread urls.

    If scrape is True, will attempt full scrape.
    Else, it will attempt to load from pickle.

    If load_pkl_path given as a string,
    it will attempt to load url_list
    from that path, or use it to save it.

    TODO:
    Possibly add a filter either at the scrape
    level or df level for english only comments.
    """
    if scrape:
        # Scrape tweets if scrape is set to true
        df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(f"{search_string}").get_items(), num_tweets))

        # Drop duplicates
        df.drop_duplicates(subset=["conversationId"], inplace=True)

        # Extract URLs
        url_list = df["rawContent"].str.findall(r"https:\S+").tolist()

        # Flatten list of lists into sorted list
        url_list = sorted([*set(itertools.chain.from_iterable(url_list))])

        # Save url_list to pickle
        if load_pkl_path:
            pickle.dump(url_list, open(load_pkl_path, "wb"))
        else:
            print("No pickle path given. Please save url_list manually.")

    else:
        # If scrape is false, try to load from pickle.
        try:
            url_list = get_processed_list(load_pkl_path)
            if len(url_list) == 0:
                print("WARNING: No URLs in list")
            else:
                print(f"Loaded url_list with {len(url_list)} urls")
        except TypeError as e:
            print(e)
            print("ERROR: Please enter valid path to load pickle from.")

    return url_list


def get_thread_content(url):
    """
    Takes in a URL and uses BeautifulSoup to extract
    the twitter thread as a list of human readable
    strings. Each entity of the list was an original
    tweet.

    TODO:
    We could consider extending the list into one
    big string if that is better. We could
    also maybe pre-process strings to remove
    certain unwanted characters.

    Output:
    List of strings
    """
    # Based on tutorial from:
    # https://hackersandslackers.com/scraping-urls-with-beautifulsoup/
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }

    # Parse initial HTML
    time.sleep(0.0001)
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, "html.parser")

    # Get tweet content tags.
    tweet_content = soup.find_all("div", class_="content-tweet", id=lambda x: x and x.startswith("tweet_"))

    # Get human readable text. This removes unwanted HTML tags.
    tweet_content = [t.get_text() for t in tweet_content]

    return tweet_content


def get_threads(url_list, processed_file_path, process_buffer=100):
    """
    Loops through list of unrolled
    tweet thread URLs and extracts
    the tweet thread content.

    Output:
    List of list of strings.
    """
    threads = get_processed_list(processed_file_list_pkl, need_dict=True)

    for i, u in enumerate(tqdm(url_list)):
        if (len(u) > 0) and (u not in threads):
            threads[u] = get_thread_content(u)

            if i % process_buffer == 0:
                pickle.dump(threads, open(processed_file_list_pkl, "wb"))

    pickle.dump(threads, open(processed_file_list_pkl, "wb"))

    return threads


if __name__ == "__main__":
    main(
        search_string=search_string,
        num_tweets=num_tweets,
        processed_file_urls_pkl=processed_file_urls_pkl,
        processed_file_list_pkl=processed_file_list_pkl,
        process_buffer=process_buffer,
    )
