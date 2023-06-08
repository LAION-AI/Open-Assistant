# Token Format

When feeding text, a prompt, and answer, and so on to the model, it's not fed as
individual letters. Instead the input is broken into tokens. Each model has its
own set of tokens ('vocab'), and each token has an id number.

Note: If you look in the json file alongside a model and look at the vocab,
you'll notice the strange letter Ġ. This is because the `bytes_to_unicode`
function takes all control and whitespace characters in code points 0-255 and
shifts them up by 256 (0x100) to make them printable. So space (code point 32
(0x20)) becomes Ġ (code point 288 (0x120)).

# Training

The LLM is initially trained by taking text from the internet, turning that into
tokens, feeding that into the LLM and have it predict the next token. This
produces a LLM model like gpt-3, galactica, etc.

## Step 1. Supervised Fine Tuning

Using a pretrained LLM, we use Supervised Fine Tuning (SFT). We take
demonstration data, in our case the Open Assistant dataset (oasst dataset)
created by volunteers, to learn a supervised policy (the SFT model) that
generates outputs from a selected list of prompts. This represents the baseline
model.

At this stage, we might also add in other datasets, but each dataset needs to be
carefully adapted to output in the format we want it to be in.

See the below section [Message Format](#message-format) for details about the
message structure that we train the SFT to use.

Note, this step would generally be done only once, just to kick-start the
process. With the two steps being done for more ongoing training.

## Step 2. Reward model (RM)

Volunteers vote on SFT model outputs, creating a new dataset consisting of
comparison data. A new model is trained on this dataset. This is the reward
model (RM).

## Step 3. Reward model

Proximal Policy Optimization (PPO) step. The reward model is used to further
fine-tune and improve the SFT model. The outcome of this step is the so-called
policy model.

# Message Format

So that the model understands who said what, we have a consistent datastructure
for communication.

There are multiple different formats, so it can get confusing.

The most up-to-date place to look for code is here:

https://github.com/Open-Assistant/oasst-model-eval/blob/main/model_eval/manual/sampling_report.py

## Message Format v2

This is used by most Open Assistant models.

Format:

```
<|prompter|>{prompt}<|endoftext|><|assistant|>
```

There is no specific prefix tag. A prefix could be placed before the first
prompter message or in the first prompter message.

Example:

```
You are a large language model that wants to be helpful<|prompter|>Hello!<|endoftext|><|assistant|>
```

Model will then reply, padding the ending with **zero or more** `<|endoftext|>`.
This is just to make entries in a batch the same size.

## Message Format v2-new

Experiments are ongoing with new Open Assistant models using this format.

**Note:** The `<|system|>{prefix}<|endoftext|>` is omitted entirely if `prefix`
is empty.

**Note:** I've added newlines and comment just for readability here. They aren't
in the format.

Format:

```
<|system|>{prefix}<|endoftext|>

# Then for each historical prompt and reply
<|prompter|>{history_prompt[i]}<|endoftext|><|assistant|>{history_reply[i]}<|endoftext|>

# Then the new prompt
<|prompter|>{prompt}<|endoftext|><|assistant|>
```

Example (newlines added for readability):

```
<|system|>You are a large language model that wants to be helpful<|system|>
<|prompter|>What is red and round?<|endoftext|><|assistant|>Hmm, a red balloon?<|endoftext|>
<|prompter|>No, smaller<|endoftext|><|assistant|>
```

Model will then reply, padding the ending with **zero or more** `<|endoftext|>`.
This is just to make entries in a batch the same size.
