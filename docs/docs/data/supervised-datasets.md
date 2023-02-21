# Supervised Datasets

For discussion about usage of supervised data see issue
<https://github.com/LAION-AI/Open-Assistant/issues/186>.

## Motivation

An important part of making the assistant useful is to teach it to understand
and follow instructions, and to perform a large set of tasks well.

While RLHF seems like the main ingredient, using existing supervised data might
help.

There are two large-scale projects in the area of instruction-following /
multitask learning: Promptsource and Natural Instructions - these projects
crowdsourced templates and turned existing NLP datasets into
instruction-following seq2seq form in natural language. They include both
long-output training examples like generating a sentence that is a likely
consequence of sentence in the prompt, and short-output, like rating prediction
from review. (Pre-)training on such datasets should help model understand and
follow instructions and teach it many abilities necessary to perform a large set
of tasks correctly. However, these data are not dialog-like - they do not look
like a normal conversation.

There are also supervised dialog datasets such as Blended Skill Talk or SODA. In
contrast to instruction-following datasets, dialog data is not as focused on
"academic tasks" or correctness, but encourage the model to respond naturally
like a person would.

### Promptsource

- GitHub: <https://github.com/bigscience-workshop/promptsource>
- paper:
  [Multitask Prompted Training Enables Zero-Shot Task Generalization](https://arxiv.org/abs/2110.08207)
- project for preparing templates and working with them
- they generated a dataset using the templates:
  - <https://huggingface.co/datasets/bigscience/P3>
  - <https://huggingface.co/datasets/bigscience/xP3> (with multilingual data but
    English prompt)
  - <https://huggingface.co/datasets/bigscience/xP3mt> (with multilingual data
    and machine-translated prompt)
- they trained zero-shot models (= models for following instructions in the
  input)
  - based on T5 architecture (encoder-decoder) called T0 family (and MT0 for
    multilingual)
  - and based on GPT architecture (decoder-only) called BloomZ family
  - Huggingface demo: [T0](https://huggingface.co/bigscience/T0pp),
    [MT0](https://huggingface.co/bigscience/mt0-large),
    [BloomZ](https://huggingface.co/bigscience/bloomz),
  - GitHub repo for T0: <https://github.com/bigscience-workshop/t-zero>
  - GitHub repo for BloomZ and MT0:
    <https://github.com/bigscience-workshop/xmtf>

### Natural instructions

- GitHub: <https://github.com/allenai/natural-instructions>
- paper:
  [Super-NaturalInstructions: Generalization via Declarative Instructions on 1600+ NLP Tasks](https://arxiv.org/abs/2204.07705)
- they crowdsource directly the data prepared for instruction following (and
  learning from a few examples)
- the GitHub repo = the dataset. It contains jsons
- they trained zero-shot and in-context few-shot models (in multiple sizes):
  - mT5 architecture (encoder-decoder, multilingual pretraining)
  - Huggingface demo few-shot:
    <https://huggingface.co/allenai/tk-instruct-3b-def-pos>
  - Huggingface demo zero-shot:
    <https://huggingface.co/allenai/tk-instruct-3b-def>

### Blended Skill Talk

- used by Facebook in Blenderbot project
- HuggingFace dataset: <https://huggingface.co/datasets/blended_skill_talk>
- example model trained on it:
  <https://huggingface.co/facebook/blenderbot_small-90M>

### SODA

- GitHub: <https://github.com/skywalker023/sodaverse>
- paper: <https://arxiv.org/abs/2212.10465>
