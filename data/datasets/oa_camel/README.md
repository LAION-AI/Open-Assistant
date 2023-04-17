Dataset Description
This is the chemistry, biology, math, and physics datasets created by CAMEL ai. https://huggingface.co/camel-ai They have been combined and converted to the Open Assistant format.

There are 110000 entries.

Languages
English

Dataset Structure
This dataset follows the OA format, which is:

INSTRUCTION (string): Instruction text
RESPONSE (string): Expected response to the instruction
SOURCE (string): Original data source short name, e.g. "wikipedia"
METADATA (JSON string, optional): Any other useful information stored in JSON
For example, NSFW content can be marked as {"nsfw": true}
The metadata contains both the topic and subtopic.

Preparing the Dataset
The dataset can be created with prepare.py. Make sure to install the required libraries inrequirements.txt!

Contributions
Converted by Check