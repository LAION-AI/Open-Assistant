# General

This page lists research papers that are relevant to the project.

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
