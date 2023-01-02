# OpenAssistant Data Schemas

## Introduction

This document describes the data schemas used by OpenAssistant. The schemas are
defined as Python classes, but can be implemented in any format, be that Python,
JSON, XML, SQL, Parquet files, etc.

Also, the schemas are leaning heavily on the
[OpenAssistant Data Structures](https://docs.google.com/presentation/d/1iaX_nxasVWlvPiSNs0cllR9L_1neZq0RJxd6MFEalUY/edit?usp=sharing)
presentation.

## Data Schemas

### Main structure: conversation trees

Conversation trees are the fundamental data structure. Many of the datasets we
want to collect can be represented as conversation trees, such as QA datasets,
chat logs, reddit dumps, etc. The main idea is that a conversation tree starts
with a prompt and branches out from there. Every node can also have metadata,
such as collected rankings, labels, or other information.

Datasets that just represent linear data, such as a list of questions and
answers, can be represented as a conversation tree with just a single branch.

```python
class ConversationTreeNode:
    text: str # The text of the node
    role: Literal['prompter', 'assistant'] # Whether the node is a user prompt/follow-up or an assistant response
    children: list[ConversationTreeNode] # The children of the node (if you have a linear conversation, this will be of length 0 or 1)
    metadata: dict[str, Any] # Node metadata (see below)

class ConversationTree:
    root: ConversationTreeNode # The node containing the initial prompt
    metadata: dict[str, Any] # Tree metadata, different from root node metadata.

```

### Metadata

Metadata encapsulates all the information that is not part of the conversation
itself. This includes data about how the node was created (i.e. where it is
from: crowd-sourced, templated, scraped, etc.), when it was created, its labels,
tags, collected rankings, and other information.

## Example: Reddit AMA dataset

- Represent each question-follow-up set as a conversation tree.
- Store things like usernames, timestamps, upvotes, etc. as metadata of the
  nodes.
- Store things like the AMA title, the AMA author, the AMA subreddit, etc. as
  metadata of the tree.

## Example: QA dataset

- Represent each question-answer pair as a conversation tree.
  - The question is the prompt, the answer is the assistant response.
- If the dataset contains multiple answers to each question, each answer can be
  a child of the question node.
- If the dataset contains context text, it can be added as metadata to the
  question node.

## Example: Templated math problem dataset

- Represent each problem as a conversation tree with the problem text as the
  prompt and the solution as the assistant response.
- Store the problem type (e.g. algebra, geometry, etc.) as metadata of the tree.
- Store the template used also as metadata of the tree, as well as the source of
  the data used to fill the template.

## File Formats

The above data should be representable in most file formats, but some care has
to be taken with respect to the recursive nature of the data.

Most row-major formats (JSON, Avro, Protobuf, etc.), as well as many databases,
have no trouble with recursive (or arbitrary) schemas, but column-major formats,
such as Parquet, do. For datasets with linear conversations, like many of the
datasets we are collecting, this is not a problem. Instead of a tree of nodes,
simply represent the conversation as a list of nodes. For true tree-like
conversations, we should use a row-major format.

## Other considerations

- For text data of moderate size, it really doesn't matter much. It's more
  important to use consistent data structures and naming, than to worry about
  the exact file format.
- For crowd-sourced data, we are collecting it into a SQL database already.
- Parquet files are a good choice for large datasets, modulo the issues with
  recursive schemas.
- If parquet can't be used, gzipped JSON-line files are a good choice. So are
  Avro files and protobufs. Keep in mind that column-major files are better for
  reading, filtering, and aggregating, but row-major files are better for
  writing.
