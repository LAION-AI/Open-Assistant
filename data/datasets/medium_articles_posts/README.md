# Medium Articles Posts Dataset

## Description

The Medium Articles Posts dataset contains a collection of articles published on the Medium platform. Each article entry includes information such as the article's title, main content or text, associated URL or link, authors' names, timestamps, and tags or categories.

## Dataset Info

The dataset consists of the following features:

- **title**: *(string)* The title of the Medium article.
- **text**: *(string)* The main content or text of the Medium article.
- **url**: *(string)* The URL or link to the Medium article.
- **authors**: *(string)* The authors or contributors of the Medium article.
- **timestamp**: *(string)* The timestamp or date when the Medium article was published.
- **tags**: *(string)* Tags or categories associated with the Medium article.

## Dataset Size

- **Total Dataset Size**: 1,044,746,687 bytes (approximately 1000 MB)

## Splits

The dataset is split into the following part:

- **Train**: 
  - Number of examples: 192,368
  - Size: 1,044,746,687 bytes (approximately 1000 MB)

## Download Size

- **Compressed Download Size**: 601,519,297 bytes (approximately 600 MB)
###   Usage example 
```python
from datasets import load_dataset
#Load the dataset
dataset = load_dataset("Falah/medium_articles_posts")

```