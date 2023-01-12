# Research

This page lists research papers that are relevant to the project.

## Table of Contents

- Reinforcement Learning from Human Feedback
- Generating Text From Language Models
- Automatically Generating Instruction Data for Training
- Uncertainty Estimation of Language Model Outputs

## Reinforcement Learning from Human Feedback <a name="reinforcement-learning-from-human-feedback"></a>

Reinforcement Learning from Human Feedback (RLHF) is a method for fine-tuning a
generative language models based on a reward model that is learned from human
preference data. This method facilitates the learning of instruction-tuned
models, among other things.

### Learning to summarize from human feedback [[ArXiv](https://arxiv.org/pdf/2009.01325.pdf)], [[Github](https://github.com/openai/summarize-from-feedback)]

> In this work, we show that it is possible to significantly improve summary
> quality by training a model to optimize for human preferences. We collect a
> large, high-quality dataset of human comparisons between summaries, train a
> model to predict the human-preferred summary, and use that model as a reward
> function to fine-tune a summarization policy using reinforcement learning.

### Training language models to follow instructions with human feedback [[ArXiv](https://arxiv.org/pdf/2203.02155.pdf)]

> Starting with a set of labeler-written prompts and prompts submitted through
> the OpenAI API, we collect a dataset of labeler demonstrations of the desired
> model behavior, which we use to fine-tune GPT-3 using supervised learning. We
> then collect a dataset of rankings of model outputs, which we use to further
> fine-tune this supervised model using reinforcement learning from human
> feedback.

### Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback [[ArXiv](https://arxiv.org/pdf/2204.05862.pdf)]

> We apply preference modeling and reinforcement learning from human feedback
> (RLHF) to finetune language models to act as helpful and harmless assistants.
> We find this alignment training improves performance on almost all NLP
> evaluations, and is fully compatible with training for specialized skills such
> as python coding and summarization.

## Generating Text From Language Models

A language model generates output text token by token, autoregressively. The
large search space of this task requires some method of narrowing down the set
of tokens to be considered in each step. This method, in turn, has a big impact
on the quality of the resulting text.

### RANKGEN: Improving Text Generation with Large Ranking Models [[ArXiv](https://arxiv.org/pdf/2205.09726.pdf)], [[Github](https://github.com/martiansideofthemoon/rankgen)]

> Given an input sequence (or prefix), modern language models often assign high
> probabilities to output sequences that are repetitive, incoherent, or
> irrelevant to the prefix; as such, model-generated text also contains such
> artifacts. To address these issues we present RankGen, a 1.2B parameter
> encoder model for English that scores model generations given a prefix.
> RankGen can be flexibly incorporated as a scoring function in beam search and
> used to decode from any pretrained language model.

## Automatically Generating Instruction Data for Training

This line of work is about significantly reducing the need for manually
annotated data for the purpose of training
[instruction-aligned](https://openai.com/blog/instruction-following/) language
models.

### SELF-INSTRUCT: Aligning Language Model with Self Generated Instructions [[ArXiv](https://arxiv.org/pdf/2212.10560.pdf)], [[Github](https://github.com/yizhongw/self-instruct)].

> We introduce SELF-INSTRUCT, a framework for improving the
> instruction-following capabilities of pretrained language models by
> bootstrapping off its own generations. Our pipeline generates instruction,
> input, and output samples from a language model, then prunes them before using
> them to finetune the original model. Applying our method to vanilla GPT3, we
> demonstrate a 33% absolute improvement over the original model on
> SuperNaturalInstructions, on par with the performance of InstructGPT-0011,
> which is trained with private user data and human annotations.

### Tuning Language Models with (Almost) No Human Labor. [[ArXiv](https://arxiv.org/pdf/2212.09689.pdf)], [[Github](https://github.com/orhonovich/unnatural-instructions)].

> In this work, we introduce Unnatural Instructions: a large dataset of creative
> and diverse instructions, collected with virtually no human labor. We collect
> 64,000 examples by prompting a language model with three seed examples of
> instructions and eliciting a fourth. This set is then expanded by prompting
> the model to rephrase each instruction, creating a total of approximately
> 240,000 examples of instructions, inputs, and outputs. Experiments show that
> despite containing a fair amount of noise, training on Unnatural Instructions
> rivals the effectiveness of training on open-source manually-curated datasets,
> surpassing the performance of models such as T0++ and Tk-Instruct across
> various benchmarks.

## Uncertainty Estimation of Language Model Outputs

### Teaching models to express their uncertainty in words [[Arxiv](https://arxiv.org/pdf/2205.14334.pdf)]

> We show that a GPT-3 model can learn to express uncertainty about its own
> answers in natural language -- without use of model logits. When given a
> question, the model generates both an answer and a level of confidence (e.g.
> "90% confidence" or "high confidence"). These levels map to probabilities that
> are well calibrated. The model also remains moderately calibrated under
> distribution shift, and is sensitive to uncertainty in its own answers, rather
> than imitating human examples.
