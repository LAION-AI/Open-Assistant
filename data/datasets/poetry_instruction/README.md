Dataset Description This dataset contains around 14,000 poems from the
PoetryFoundation.org site. They are converted to question:response pairs, using
the tags as topics. 5% of the dataset is titling requests -- the user provides a
poem and asks the assistant to title it.

It can be found here, on my HuggingFace -
https://huggingface.co/datasets/checkai/instruction-poems

Languages English

Dataset Structure This dataset follows the OA format, which is:

INSTRUCTION (string): The user asks for a poem (from a variety of premade
prompts) with topics (tags). If the given poem has no tags, the user asks for a
poem on its own.

RESPONSE (string): The assistant replies with the poem and title (from a variety
of premade prompts).

SOURCE (string): The source is PoetryFoundation.org and the poet's name.

METADATA (JSON String): {"author": "author of the original poem", "title":
"title of the poem", "tags": "tags from poetry foundation."}

Preparing the Dataset The dataset can be created with prepare.py. Make sure to
install the required libraries in requirements.txt!

Contributions Created by Check Original dataset source -
https://www.kaggle.com/datasets/tgdivy/poetry-foundation-poems
