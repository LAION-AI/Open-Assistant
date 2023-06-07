# ManySStuBs4J Dataset

The ManySStuBs4J corpus is a collection of simple fixes to Java bugs, designed
for evaluating program repair techniques. We collect all bug-fixing changes
using the SZZ heuristic, and then filter these to obtain a data set of small bug
fix changes.

It contains over 3 million bugs, so the benefit from it would be substantial.

It is easy to put it into dialogue form:

User: Find the bug in the following code: {CODE} Reply: The bugfix can be
described as follows: {COMMIT_MESSAGE} The fixed code is: {FIXED-CODE}

It would be a substantial boost to our dataset as far as code is concerned.

As for now, I create prompts only with broken and fixed code, without commit
messages that must be scraped from GitHub. Still it should be very useful.

# Notebook on Colab

Here is the Google Colab code to generate the prompts from the dataset:
https://colab.research.google.com/drive/16Fr4iW0x1JdPC8x6GiBb6b4YtEr1CDGH?authuser=4#scrollTo=GFt0SJ1vpMPR

## Contributing

Adding a way to incorporate commit messages into the prompts would be a great
contribution. This can be done by scraping the GitHub API for the commit
messages based on the commit hash, or by downloading the repository with the
full history and extracting the commit messages from there.
