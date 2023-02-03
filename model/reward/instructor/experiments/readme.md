# T5-flan-xxl-encoder experiment
## Description
Fine-tune the T5-flan encoder into a reward model
Add MLP at the bottom of T5-encoder, and using a manually labeled dataset, given one question and two responses at a time, the model is trained to correctly discern which response is better, through the manually labeled preferences.

## Datasets

[webGPT](https://huggingface.co/datasets/openai/webgpt_comparisons)

[HFsummary](https://github.com/openai/summarize-from-feedback)

[synthetic-GPT-J](https://huggingface.co/datasets/Dahoas/synthetic-instruct-gptj-pairwise/)


## Process

For convenience of notation, $Q$, $A_p$, $A_n$, denote the question, good answer, and bad answer of a single piece of data in the manually labeled data, respectively.

Use [T5-flan-small](https://huggingface.co/google/flan-t5-base) encoder part of the training model, again add a MLP at the end of this section, using contrasive Loss as the Loss function, Use Adam as the optimizer.

Two calculation flows are used:

1. Concatenate $Q$and $A$into A sentence to get $S$, add vectors representing question and answer before $Q$and $A$respectively, and then use the model to encode $S$to get $S'$. Finally, $S_n'$and $S_p'$are given to the MLP for classification.

2. The model to answer after coding $A_p '$and $A_n' $1 after encoding padding to the problem of $Q '$as dimensions, using MLP $A_p' $, $A_n '$, and $Q $mapped to get consistent dimension $A_p' $, $A_n '$,' $, and $Q Then, the normalized $A_p "$and $A_n" $dot products the normalized $Q "$respectively to get $r_p$and $r_n$. These two values represent the correlation between the answer and the question. If $r_p$is greater than $r_n$, it indicates that the model prediction is correct.

The model is trained on the above dataset, and the accuracy of the model is tested on the WebGPT validation set.



## results

| Model with MLP| WebGPT Accuracy |
| ----------- | --------- |
| T5 - flan - small | 53.2%|
| T5 - flan - base |  48.3%|
| T5 - flan - large | 54.6%|
| T5 - flan - XXL | 47.9%|



An accuracy of around 50% indicates that the model is not working, that the model is not getting better as the number of parameters increases, and that the whole model structure and training method are wrong.



## Ideas

The feasibility was only roughly verified in the training process, and the hyperparameters and specific structure of the model were not studied in detail.

For the reward model, the limitations of the transformer architecture itself may not be suitable for judging the quality of two responses, and a model based on adversarial learning such as Electra-Discriminator should achieve better results.

 
