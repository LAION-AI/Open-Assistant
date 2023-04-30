# Twitter data collection for Open Assistant

Conversations on Twitter can be an interesting and useful source of data for our
model to learn from. Certain twitter threads may contain helpful prompts and
replies, in a similar fashion to how we want our model to be able to respond to
prompts in a useful way.

Thus, these scripts are intended to process twitter data from a variety of
sources, process them into cleaner and more useful formats, and then combine the
various outputs into a unified training set that can be fed to our model as a
conversation, or at least as a prompt with replies.

**Note: Based on issue #126**

## Possible Data Paths

- Twitterstream archive: https://archive.org/details/twitterstream These are
  large .tar files with compressed json files inside. However, some data points
  such as reply counts seem to always be 0 due to limitations when scraping the
  Twitter API.
- Alternative APIs such as snscrape, twint, etc. These alternative APIs often
  are harder to use than the official Twitter API but can often bypass API
  limits which can make it useful for larger scale data collection. The downside
  is potentially slower speed, and less features.
- The official Twitter API

## Currently Completed Items

- Downloaded various archive files (both are .tar, but each have a different
  format of json compression. One used .gz, and the other.bz2). Each json file
  is roughly 2000 rows of tweets. There are thousands of these compressed json
  files. Managing the IO of opening lots of small files is one of the
  challenges, which is why future steps will consolidate data into larger easier
  to process files.
- Wrote script that can loop through the compressed json files, cleans them up a
  bit by removing truncated tweets or tweets that aren't replies. The script
  then standardizes the columns, and exports the polars dataframes into parquet
  files for future processing. Note: Using polars instead of pandas due to
  performance reasons.
- Wrote scripts that process the large dump of tweets into conversation threads
  using the tree and node architecture. This results in aroun 17K conversation
  threads bassed on a dump of 90M tweets.
- Script can output the conversation threads into a jsonl file for further
  filtering or use in models.

## Main Issue

- The issue is that we can easily scrape replies, but there is no guarantee the
  original tweet is in the archive file. Furthermore, the archives are large so
  they would need to be kept completely in-memory or in a db to reference. We
  still need to decide if we want to try to mine the archive to piece together
  the conversations, or we can take the list of replied tweets and loop through
  those and use alternative apis to fetch the original tweet text, and then
  match it with the confirmed replies already in our archive to generate the
  prompt/replies data. Currently, my script can extract conversations based on
  the dump, but it is a small percentage of the overall dump, and there is no
  guarantee of the quality of the tweets.
- The tweet quality is the other major issue. We can get conversations through
  the currently made scripts, but they most likely don't match a useful
  instruction -> fulfillment. We are trying to filter the tweets through various
  means such as matching useful hashtags, or by using cosine similarity against
  known instructions.
- The modern Twitter API has conversation_id as a field which can be a way to
  gather all tweets in a thread sort of automatically although there is
  pagination limits. The main issue with this is it seems hard to search for it
  using alternative APIs.

## TODO

- Write scripts to filter existing conversations into useful instructions ->
  fulfillment with hashtags or cosine similarity.
- Train model to detect if text is a suitable instruction. This could then be
  run through the conversations (or full tweet dump) to simplify the process.
  Related to issue #143.
- Write script that matches the original tweets and their text with the archive
  data to create the prompt/reply dataset. (Optional)
- Decide on final output format and storage options for the dataset. Currently
  in JSONL with tree / node architecture as python dicts which is acceptable I
  believe.
- Alternatively: Store processed tweets into DB or alternative option.(Optional)
