# Open Assistant Data Module (oasst_data)

## Installation of oasst_data

If you got the exception `ModuleNotFoundError: No module named 'oasst_data'` you
first need to install the `oasst_data` package:

Run `pip install -e .` in the `oasst-data/` directory of the Open-Assistant
repository to install the `oasst_data` python package in editable mode.

## Reading Open-Assistant Export Files

Reading jsonl files is in general very simple in Python. To further simplify the
process for OA data the `oasst_data` module comes with Pydantic class
definitions for validation and helper functions to load and traverse message
trees.

Code example:

```python
# parsing OA data files with oasst_data helpers
from oasst_data import load_trees, visit_messages_depth_first, ExportMessageNode

messages: list[ExportMessageNode] = []

input_file_path = "data_file.jsonl.gz"
for tree in load_trees(input_file_path):
    if tree.prompt.lang not in ["en","es"]:     # filtering by language tag (optional)
        continue

    # example use of depth first tree visitor help function
    visit_messages_depth_first(tree.prompt, visitor=messages.append, predicate=None)
```

A more comprehensive example of loading all conversation threads ending in
assistant replies can be found in the file
[oasst_dataset.py](https://github.com/LAION-AI/Open-Assistant/blob/main/model/model_training/custom_datasets/oasst_dataset.py)
which is used to load Open-Assistant export data for supervised fine-tuning
(training) of our language models.

You can also load jsonl data completely without dependencies to `oasst_data`
solely with standard python libraries. In this case the json objects are loaded
as nested dicts which need to be 'parsed' manually by you:

```python
# loading jsonl files without using oasst_data
import gzip
import json
from pathlib import Path

input_file_path = Path(input_file_path)
if input_file_path.suffix == ".gz":
    file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
else:
    file_in = input_file_path.open("r", encoding="UTF-8")

with file_in:
    # read one object per line
    for line in file_in:
        dict_tree = json.loads(line)
        # manual parsing of data now goes here ...
```

## Open-Assistant JSON Lines Export Data Format

Open-Assistant export data is written as standard
[JSON Lines data](https://jsonlines.org/). The generated files are UTF-8 encoded
text files with single JSON objects in each line. The files come either
uncompressed with the ending `.jsonl` or compressed with the ending `.jsonl.gz`.

Three different types of objects can appear in these files:

1. Individual Messages
2. Conversation Threads
3. Message Trees

For readability the following JSON examples are shown formatted with indentation
on multiple lines although they are be stored without indentation in the actual
data file.

### 1. Individual Messages

Message objects can be identified by the presence of a `"message_id"` property.
In files written by Open-Assistant this property will appear as the first
property on the line directly after the opening curly brace.

Each message needs at least an id (UUID), message text, a role (either
"prompter" or "assistant") and a language tag
([BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag)) like "en" for
English.

Minimal example of a message:

```json
{
  "message_id": "13714ad5-3161-4ead-9593-7248b0a3f218",
  "text": "List the pieces of a reinforcement learning system (..)",
  "role": "prompter",
  "lang": "en"
}
```

Example of a message with more properties:

```json
{
    "message_id": "218440fd-5317-4355-91dc-d001416df62b",
    "parent_id": "13592dfb-a6f9-4748-a92c-32b34e239bb4",
    "user_id": "8e95461f-5e94-4d8b-a2fb-d4717ce973e4",
    "text": "It was the winter of 2035, and artificial intelligence (..)",
    "role": "assistant",
    "lang": "en",
    "review_count": 3,
    "review_result": true,
    "deleted": false,
    "rank": 0,
    "synthetic": true,
    "model_name": "oasst-sft-0_3000,max_new_tokens=400 (..)",
    "labels": {
        "spam": { "value": 0.0, "count": 3 },
        "lang_mismatch": { "value": 0.0, "count": 3 },
        "pii": { "value": 0.0, "count": 3 },
        "not_appropriate": { "value": 0.0, "count": 3 },
        "hate_speech": { "value": 0.0, "count": 3 },
        "sexual_content": { "value": 0.0, "count": 3 },
        "quality": { "value": 0.416, "count": 3 },
        "toxicity": { "value": 0.16, "count": 3 },
        "humor": { "value": 0.0, "count": 3 },
        "creativity": { "value": 0.33, "count": 3 },
        "violence": { "value": 0.16, "count": 3 }
    }
},
```

The backend export tool
([export.py](https://github.com/LAION-AI/Open-Assistant/blob/main/backend/export.py))
will generate jsonl files with individual messages when a set of messages is
exported that is not a full tree. This is for example the case when filtering
messages based on properties like user, deleted, spam or synthetic. Spam
messages are those which have a `review_result` that is `false`.

### 2. Conversation Threads

Conversation threads are a linear lists of messages. THese objects can be
identified by the presence of the `"thread_id"` property which contains the UUID
of the last messsage of the the thread (which can be used to reconstruct the
thread by returning the list of ancestor messages up to the prompt root
message). The message_id of the first message is normally also the id of the
message-tree that contains the thread.

```json
{
  "thread_id": "534c7711-afb5-4410-9006-489dc885280e",
  "thread": [
    {
      "message_id": "14fbb664-a620-45ce-bee4-7c519b16a793",
      "text": "Why can't we divide by 0? (..)",
      "role": "prompter",
      "lang": "en"
    },
    {
      "message_id": "894d30b6-56b4-4605-a504-89dd15d4d1c8",
      "text": "The reason we cannot divide by zero is because (..)",
      "role": "assistant",
      "lang": "en"
    },
    {
      "message_id": "1c9210e9-af9e-4507-abc5-3b3c7bca4dce",
      "text": "Can you explain why we created a definition (..)",
      "role": "prompter",
      "lang": "en"
    },
    {
      "message_id": "534c7711-afb5-4410-9006-489dc885280e",
      "text": "The historical origin of the imaginary (..)",
      "role": "assistant",
      "lang": "en"
    }
  ]
}
```

### 3. Message Trees

Message trees have of a prompt message at the root and can then branch out into
multiple different reply branches which each can again have further replies.
Message trees can be identified by the `"message_tree_id"` property. The
`message_tree_id` always matches the id of the prompt-message.

Example of a tree with minimal messages:

For clarity only the mandatory elements of the message are shown here. The full
export format contains all the message attributes as shown above in the full
message example.

```json
{
  "message_tree_id": "14fbb664-a620-45ce-bee4-7c519b16a793",
  "tree_state": "ready_for_export",
  "prompt": {
    "message_id": "14fbb664-a620-45ce-bee4-7c519b16a793",
    "text": "Why can't we divide by 0? (..)",
    "role": "prompter",
    "lang": "en",
    "replies": [
      {
        "message_id": "894d30b6-56b4-4605-a504-89dd15d4d1c8",
        "text": "The reason we cannot divide by zero is because (..)",
        "role": "assistant",
        "lang": "en",
        "replies": [
          {
            "message_id": "1c9210e9-af9e-4507-abc5-3b3c7bca4dce",
            "text": "Can you explain why we created a definition (..)",
            "role": "prompter",
            "lang": "en",
            "replies": [
              {
                "message_id": "534c7711-afb5-4410-9006-489dc885280e",
                "text": "The historical origin of the imaginary (..)",
                "role": "assistant",
                "lang": "en",
                "replies": []
              },
              {
                "message_id": "bb791a11-2de2-4e39-9b99-55da5cc730a0",
                "text": "The square root of -1, denoted i, was (..)",
                "role": "assistant",
                "lang": "en",
                "replies": []
              }
            ]
          }
        ]
      },
      {
        "message_id": "84d0913b-0fd9-4508-8ef5-205626a7039d",
        "text": "The reason that the result of a division by zero is (..)",
        "role": "assistant",
        "lang": "en",
        "replies": [
          {
            "message_id": "3352725e-f424-4e3b-a627-b6db831bdbaa",
            "text": "Math is confusing. Like those weird Irrational (..)",
            "role": "prompter",
            "lang": "en",
            "replies": [
              {
                "message_id": "f46207ca-3149-46e9-a466-9163d4ce499c",
                "text": "Irrational numbers are simply numbers (..)",
                "role": "assistant",
                "lang": "en",
                "replies": []
              },
              {
                "message_id": "d63d5610-338b-46b1-b537-9211cdb0ddc6",
                "text": "Irrational numbers can be confusing (..)",
                "role": "assistant",
                "lang": "en",
                "replies": []
              },
              {
                "message_id": "0ef7430e-314a-4da1-92bd-49a6967dc22f",
                "text": "Irrational numbers are real numbers (..)",
                "role": "assistant",
                "lang": "en",
                "replies": []
              }
            ]
          }
        ]
      }
    ]
  }
}
```

This format is used when whole trees are exported with
[export.py](https://github.com/LAION-AI/Open-Assistant/blob/main/backend/export.py)
(for example all trees in `ready_to_export` state).
