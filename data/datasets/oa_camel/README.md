Dataset Description
This is the chemistry, biology, math, and physics datasets created by CAMEL ai. https://huggingface.co/camel-ai. They have been combined and converted to the Open Assistant format.

There are 110000 entries.

Languages
English

Dataset Structure
This dataset follows the OA format, which is:

INSTRUCTION (string): This is the "message_1" from the original dataset, which is the user's question.

RESPONSE (string): "message_2" from original dataset, which is the assistant response.

SOURCE (string): The source is the name of the dataset the entry is sourced from (for example, "camel-ai/chemistry").

METADATA (JSON String):
{"Topic": "Topic sourced from the original dataset",
"Sub-Topic": "More detailed Sub-Topic from original dataset"}

Preparing the Dataset
The dataset can be created with prepare.py. Make sure to install the required libraries in requirements.txt!

Contributions
Converted by Check