# StackExchange Builder

StackExchange Builder is a notebook that downloads data from StackExchange data
dumps and converts it into different formats. It will parse the XML files, group
questions and answers, can filter the dataset and puts the results into the
Open-Assistant Data Scheme. Files can be saved to either JSON, JSONL, Parquet,
or CSV.

---

#### Sample Data Open-Assistant Data Scheme:

Open-Assistant Data Scheme as outlined here:
https://github.com/LAION-AI/Open-Assistant/blob/main/docs/data_schemas.md

```
{
    "root": {
        "text": "Science Fiction has frequently shown AI to be a threat to the very existence of mankind. AI systems have often been the antagonists...",
        "role": "prompter",
        "children": [
            {
                "text": "Nothing.  \nIts in almost everyone's favor for it to stay that way financially. Having non-technical individuals associate AI with terminators...",
                "role": "assistant",
                "children": [],
                "metadata": {
                    "AnswerScore": 2.0,
                    "AcceptedAnswerFlag": true
                }
            }
        ],
        "metadata": {
            "QuestionScore": 5,
            "QuestionTags": "social, artificial consciousness"
        }
    },
    "metadata": {
        "Title": "\"AI will kill us all! The machines will rise up!\" - what is being done to dispel such myths?",
        "QuestionContentLicense": "CC BY-SA 4.0",
        "DataSource": "https://ia600107.us.archive.org/view_archive.php?archive=/27/items/stackexchange/ai.stackexchange.com.7z&file=Posts.xml",
        "CreationDate": "2019-10-16T13:57:37.143"
    }
}
```

---

#### JSONL format

Each question and all related answers are on a single line in JSONL format.

```
{
    "Title": "1 hidden layer with 1000 neurons vs. 10 hidden layers with 100 neurons",
    "Question": "These types of questions may be problem-dependent...",
    "QuestionScore": 16,
    "QuestionTags": "neural networks",
    "QuestionContentLicense": "CC BY-SA 3.0",
    "DataSource": "https://ia600107.us.archive.org/view_archive.php?archive=/27/items/stackexchange/ai.stackexchange.com.7z&file=Posts.xml",
    "CreationDate": "2017-05-04T13:06:37.990",
    "Answers": [
        {
            "Answer": "Basically, having multiple layers (aka a deep network) makes your network more eager to recognize certain aspects of input data...",
            "AnswerScore": 13.0,
            "AcceptedAnswerFlag": true
        },
        {
            "Answer": "There are so many aspects.\n1. Training:\nTraining deep nets is a hard job due to the vanishing (rearly exploding) gradient problem...",
            "AnswerScore": 4.0,
            "AcceptedAnswerFlag": false
        },
        {
            "Answer": "If the problem you are solving is linearly separable, one layer of 1000 neurons can do better job...",
            "AnswerScore": 1.0,
            "AcceptedAnswerFlag": false
        },
        {
            "Answer": "\nI think you have a confusion in the basics of the neural networks.\n  Every layer has a separate activation...",
            "AnswerScore": 0.0,
            "AcceptedAnswerFlag": false
        }
    ]
}
```

#### Table/CSV/Parquet Format

There are a lot more columns left over in the table format. `_q` and `_a` are
suffixes indicating if the column came from the question or answer table as
leftover from a join statement.

```
|  Id_q |                                          Question | ParentId_a | AcceptedAnswerId |    Id_a |                                            Answer | AnswerScore | AcceptedAnswerFlag |
|------:|--------------------------------------------------:|-----------:|-----------------:|--------:|--------------------------------------------------:|------------:|-------------------:|
| 15730 | As a human being, we can think infinity. In pr... |    15730.0 |            15744 | 15744.0 | I think this is a fairly common misconception ... |        62.0 |               True |
| 15730 | As a human being, we can think infinity. In pr... |    15730.0 |            15744 | 15753.0 | I think your premise is flawed.\nYou seem to a... |        19.0 |              False |
| 15730 | As a human being, we can think infinity. In pr... |    15730.0 |            15744 | 15747.0 | TL;DR: The subtleties of infinity are made app... |        12.0 |              False |
| 15730 | As a human being, we can think infinity. In pr... |    15730.0 |            15744 | 15756.0 | In Haskell, you can type:\nprint [1..]\nand it... |         9.0 |              False |
```

---

## Contributing

Feel free to contribute to this notebook. It's not perfect and additional
functionality is planned.
