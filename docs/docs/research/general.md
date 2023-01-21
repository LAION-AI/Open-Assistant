# Research

This page lists research papers that are relevant to the project.

## Table of Contents

- Reinforcement Learning from Human Feedback
- Generating Text From Language Models
- Automatically Generating Instruction Data for Training
- Uncertainty Estimation of Language Model Outputs
- Evidence-Guided Text Generation
- Reward Model Optimization
- Dialogue-Oriented RLHF
- Reduce Harms in Language Models

## Reinforcement Learning from Human Feedback

Reinforcement Learning from Human Feedback (RLHF) is a method for fine-tuning a
generative language models based on a reward model that is learned from human
preference data. This method facilitates the learning of instruction-tuned
models, among other things.

### Fine-Tuning Language Models from Human Preferences [[ArXiv](https://arxiv.org/abs/1909.08593)], [[GitHub](https://github.com/openai/lm-human-preferences)]

> In this paper, we build on advances in generative pretraining of language
> models to apply reward learning to four natural language tasks: continuing
> text with positive sentiment or physically descriptive language, and
> summarization tasks on the TL;DR and CNN/Daily Mail datasets. For stylistic
> continuation we achieve good results with only 5,000 comparisons evaluated by
> humans. For summarization, models trained with 60,000 comparisons copy whole
> sentences from the input but skip irrelevant preamble.

### Learning to summarize from human feedback [[ArXiv](https://arxiv.org/abs/2009.01325)], [[GitHub](https://github.com/openai/summarize-from-feedback)]

> In this work, we show that it is possible to significantly improve summary
> quality by training a model to optimize for human preferences. We collect a
> large, high-quality dataset of human comparisons between summaries, train a
> model to predict the human-preferred summary, and use that model as a reward
> function to fine-tune a summarization policy using reinforcement learning.

### Recursively Summarizing Books with Human Feedback [[ArXiv](https://arxiv.org/abs/2109.10862)]

> Our method combines learning from human feedback with recursive task
> decomposition: we use models trained on smaller parts of the task to assist
> humans in giving feedback on the broader task. We collect a large volume of
> demonstrations and comparisons from human labelers. Our resulting model
> generates sensible summaries of entire books, even matching the quality of
> human-written summaries in a few cases (∼5% of books). We achieve
> state-of-the-art results on the recent BookSum dataset for book-length
> summarization. We release datasets of samples from our model.

### Training language models to follow instructions with human feedback [[ArXiv](https://arxiv.org/abs/2203.02155)]

> Starting with a set of labeler-written prompts and prompts submitted through
> the OpenAI API, we collect a dataset of labeler demonstrations of the desired
> model behavior, which we use to fine-tune GPT-3 using supervised learning. We
> then collect a dataset of rankings of model outputs, which we use to further
> fine-tune this supervised model using reinforcement learning from human
> feedback.

### Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback [[ArXiv](https://arxiv.org/abs/2204.05862)]

> We apply preference modeling and reinforcement learning from human feedback
> (RLHF) to finetune language models to act as helpful and harmless assistants.
> We find this alignment training improves performance on almost all NLP
> evaluations, and is fully compatible with training for specialized skills such
> as python coding and summarization.

### Self-critiquing models for assisting human evaluators [[ArXiv](https://arxiv.org/abs/2206.05802)]

> We fine-tune large language models to write natural language critiques
> (natural language critical comments) using behavioral cloning. On a
> topic-based summarization task, critiques written by our models help humans
> find flaws in summaries that they would have otherwise missed. We study
> scaling properties of critiquing with both topic-based summarization and
> synthetic tasks. Finally, we motivate and introduce a framework for comparing
> critiquing ability to generation and discrimination ability. These results are
> a proof of concept for using AI-assisted human feedback to scale the
> supervision of machine learning systems to tasks that are difficult for humans
> to evaluate directly. We release our training datasets.

### Is Reinforcement Learning (Not) for Natural Language Processing?: Benchmarks, Baselines, and Building Blocks for Natural Language Policy Optimization [[ArXiv](https://arxiv.org/abs/2210.01241)]

> We tackle the problem of aligning pre-trained large language models (LMs) with
> human preferences. We present the GRUE (General Reinforced-language
> Understanding Evaluation) benchmark, a set of 6 language generation tasks
> which are supervised by reward functions which capture automated measures of
> human preference. Finally, we introduce an easy-to-use, performant RL
> algorithm, NLPO (Natural Language Policy Optimization) that learns to
> effectively reduce the combinatorial action space in language generation. We
> show that RL techniques are generally better than supervised methods at
> aligning LMs to human preferences.

## Generating Text From Language Models

A language model generates output text token by token, autoregressively. The
large search space of this task requires some method of narrowing down the set
of tokens to be considered in each step. This method, in turn, has a big impact
on the quality of the resulting text.

### RANKGEN: Improving Text Generation with Large Ranking Models [[ArXiv](https://arxiv.org/abs/2205.09726)], [[GitHub](https://github.com/martiansideofthemoon/rankgen)]

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

### SELF-INSTRUCT: Aligning Language Model with Self Generated Instructions [[ArXiv](https://arxiv.org/abs/2212.10560)], [[GitHub](https://github.com/yizhongw/self-instruct)].

> We introduce SELF-INSTRUCT, a framework for improving the
> instruction-following capabilities of pretrained language models by
> bootstrapping off its own generations. Our pipeline generates instruction,
> input, and output samples from a language model, then prunes them before using
> them to finetune the original model. Applying our method to vanilla GPT3, we
> demonstrate a 33% absolute improvement over the original model on
> SuperNaturalInstructions, on par with the performance of InstructGPT-0011,
> which is trained with private user data and human annotations.

### Tuning Language Models with (Almost) No Human Labor. [[ArXiv](https://arxiv.org/abs/2212.09689)], [[GitHub](https://github.com/orhonovich/unnatural-instructions)].

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

### Teaching models to express their uncertainty in words [[ArXiv](https://arxiv.org/abs/2205.14334)]

> We show that a GPT-3 model can learn to express uncertainty about its own
> answers in natural language -- without use of model logits. When given a
> question, the model generates both an answer and a level of confidence (e.g.
> "90% confidence" or "high confidence"). These levels map to probabilities that
> are well calibrated. The model also remains moderately calibrated under
> distribution shift, and is sensitive to uncertainty in its own answers, rather
> than imitating human examples.

## Evidence-Guided Text Generation

### WebGPT: Browser-assisted question-answering with human feedback [[ArXiv](https://arxiv.org/abs/2112.09332)]

> We fine-tune GPT-3 to answer long-form questions using a text-based
> web-browsing environment, which allows the model to search and navigate the
> web. We are able to train models on the task using imitation learning, and
> then optimize answer quality with human feedback. Models must collect
> references while browsing in support of their answers. Our best model is
> obtained by fine-tuning GPT-3 using behavior cloning, and then performing
> rejection sampling against a reward model.

### Teaching language models to support answers with verified quotes [[ArXiv](https://arxiv.org/abs/2203.11147)]

> In this work we use RLHF to train "open-book" QA models that generate answers
> whilst also citing specific evidence for their claims, which aids in the
> appraisal of correctness. Supporting evidence is drawn from multiple documents
> found via a search engine, or from a single user-provided document. However,
> analysis on the adversarial TruthfulQA dataset shows why citation is only one
> part of an overall strategy for safety and trustworthiness: not all claims
> supported by evidence are true.

## Reward Model Optimization

### Scaling Laws for Reward Model Overoptimization [[ArXiv](https://arxiv.org/abs/2210.10760)], [[Preceding Blogpost](https://openai.com/blog/measuring-goodharts-law/)]

> In this work, we use a synthetic setup in which a fixed "gold-standard" reward
> model plays the role of humans, providing labels used to train a proxy reward
> model. We study how the gold reward model score changes as we optimize against
> the proxy reward model using either reinforcement learning or best-of-n
> sampling. We study the effect on this relationship of the size of the reward
> model dataset. We explore the implications of these empirical results for
> theoretical considerations in AI alignment.

## Dialogue-Oriented RLHF

### Dynamic Planning in Open-Ended Dialogue using Reinforcement Learning [[ArXiv](https://arxiv.org/abs/2208.02294)]

> Building automated agents that can carry on rich open-ended conversations with
> humans "in the wild" remains a formidable challenge. In this work we develop a
> real-time, open-ended dialogue system that uses reinforcement learning (RL) to
> power a bot's conversational skill at scale. Trained using crowd-sourced data,
> our novel system is able to substantially exceeds several metrics of interest
> in a live experiment with real users of the Google Assistant.

### Improving alignment of dialogue agents via targeted human judgements [[ArXiv](https://arxiv.org/abs/2209.14375)]

> We present Sparrow, an information-seeking dialogue agent trained to be more
> helpful, correct, and harmless compared to prompted language model baselines
> First, to make our agent more helpful and harmless, we break down the
> requirements for good dialogue into natural language rules the agent should
> followy. Second, our agent provides evidence from sources supporting factual
> claims when collecting preference judgements over model statements.Finally, we
> conduct extensive analyses showing that though our model learns to follow our
> rules it can exhibit distributional biases.

## Reduce Harms in Language Models

### Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned [[ArXiv](https://arxiv.org/abs/2209.07858)]

> We investigate scaling behaviors for red teaming. We find that the RLHF models
> are increasingly difficult to red team as they scale, and we find a flat trend
> with scale for the other model types. We exhaustively describe our
> instructions, processes, statistical methodologies, and uncertainty about red
> teaming.
