# Writing Prompt

Writing prompt folder has a notebook that entails the pipeline to take samples
of [Writing Prompt](https://www.kaggle.com/datasets/ratthachat/writing-prompts)
dataset and augment that collection with some small transformations into a
prompt, having the same story as a response.

This process required the summarization of text that was executed by one A100
GPU running [T5](pszemraj/long-t5-tglobal-base-16384-book-summary) model.

The sample created was delivered at
[Hugging Face dataset](https://huggingface.co/datasets/fabraz/writingPromptAug/),
where you will find more details.

## Contributing

Feel free to contribute to this notebook.
