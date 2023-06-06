This dataset is a template generated instructional Python datastet generated
from an annotated version of the code-search-net dataset. The annotated version
of code-search-net dataset can be found
[here](https://huggingface.co/datasets/Nan-Do/code-search-net-python).

The dataset contains around 450000 python annotated functions. The dataset is
split into two blocks, one in which the task is starting from the annotated
summary to generate an instruction to generate the code as a response, and
another one in which the expected response is to generate a description of the
function or a docstring. For the second block the docstring has been removed
from the function from 90% of the samples. To generate the summaries this
[model](https://huggingface.co/Salesforce/codet5-base-codexglue-sum-python) has
been used.

**Note**: some summarisation tasks are very easy because the prompt already
contains a docstring in the function which is then used as the ground truth
response. It may be useful to filter these in future. (All the docstrings have
been removed now)

### Summarize_codesearchnet_for_python.ipynb

This notebook is used to generate the python annotated version of the
code-search-net dataset for Python

### GenerateOpenAssistantInstructionResponseFormat.ipynb

This notebook is used to generate the Open-Assistant instructional dataset
