# Cohere Grounded QA

[Cohere AI created a question-answering chatbot](https://github.com/cohere-ai/sandbox-grounded-qa)
that can

1. Understand questions in the context of a conversation
2. Search the internet for related information
3. Identify which information in the search results is relevant to the question
4. Synthesize the information into an answer to the question

## Cohere API

[Cohere's generate function](https://docs.cohere.ai/reference/generate):
Continues a text prompt using either the `medium` or `xlarge` model.

[Cohere's embed function](https://docs.cohere.ai/reference/embed): Embedgs a
list of strings using either the `small` or `large` model. Alternatively, you
can specify the ID of a custom model and use that instead.

## Grounded QA System

Cohere's Grounded QA system makes 4 calls to the Cohere API:

1. Get contextualized question as a query to Google
   ([code](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/model.py))

   - Input: Chat History
   - Output: Contextualized Question
   - API Call: `cohere.generate`
   - Model: `xlarge`
   - [Prompt](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/prompt_data/get_contextual_search_query.prompt):
     Nine few-shot examples of (Chat History, Contextualized Question) pairs
     followed by the current chat history and the prompt "question: "

2. Generate sample answer to compare with search results
   ([code](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/model.py))

   - Input: Contextualized Question
   - Output: Sample Answer
   - API Call: `cohere.generate`
   - Model: `xlarge`
   - [Prompt](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/prompt_data/get_sample_answer.prompt):
     Some task instructions followed by 12 few-shot examples of (Contextualized
     Question, Sample Answer) pairs followed by the current contextualized
     question and the prompt "answer: "

3. Get embeddings to rank search results by cosine similarity to sample answer
   ([code](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/search.py))

   - Input: Sample Answer, Search Results
   - Output: Embeddings of sample answer and all search result documents
   - API Call: `cohere.embed`
   - Model: `multilingual-22-12`

4. Condition on the top 2 most similar search results and answer the question
   ([code](https://github.com/cohere-ai/sandbox-grounded-qa/blob/main/qa/answer.py))
   - Input: Top 2 Search Results, Contextualized Question
   - Output: Answer
   - API Call: `cohere.generate`
   - Model: `xlarge`
   - [Prompt](https://github.com/cohere-ai/sandbox-grounded-qa/blob/43f3e9710112dcc8c92652ac1326ed9330823ddf/qa/answer.py#L25):
     Task instructions followed by the context and question.

## Models

Cohere's model documentation is pretty sparse

### [xlarge](https://docs.cohere.ai/docs/generation-card#model-description)

- Training Data:
  [`coheretext-filtered` dataset](https://docs.cohere.ai/docs/data-statement)
  - 200GB of filtered text (3TB unfiltered) from the Google Books dataset,
    CommonCrawl, and text scraped by Cohere
  - English documents only
  - Filtered "harmful, biased, or otherwise undesirable documents"
- Model architecture: Generative Pretrained Transformer
- Model Performance:
  - Hellaswag Accuracy, Zero-Shot: 0.805
  - PIQA Likelihood, Zero-Shot: 0.824
  - Cohere also reported
    [safety benchmarks](https://docs.cohere.ai/docs/generation-card#safety-benchmarks)

### [multilingual-22-12](https://docs.cohere.ai/docs/multilingual-language-models)

- Multilingual model was trained using dot product calculations
- Model Performance:
  - Clustering: 51.0
  - Search-English: 55.8
  - Search-Multilingual: 51.4
  - Cross-lingual Classification: 64.6
  - Cohere's multilingual model outperformed: Sentence-transformers:
    `paraphrase-multilingual-mpnet-base-v2`, Google: `LaBSE`, Google:
    `Universal Sentence Encoder` in all the above categories according to
    Cohere.

## OpenAssistant for Grounded QA

OpenAssistant may fulfill a similar role as the `xlarge` Cohere model in the
grounded QA system if it can:

1. Generate a contextualized question from a chat history
2. Generate a sample answer to compare with search results
3. Generate an answer conditioned on the top 2 most similar search results

Perhaps these tasks could be work packages and get assigned to human annotators
to create examples of the input and output for each task.

OpenAssistant must also be able to identify when it is appropriate to search the
internet. The Cohere system assumes every message from the user is a question
and searches the internet for an answer. OpenAssistant would also need a way to
indicate to an internal system that it "wants" to search the internet.

Perhaps OpenAssistant could prefix every message it sends with a recipient ID.
If it wishes to send a command to an internal system, if could prefix the
message with something like CMD: whereas if it wants to communicate with the
user, it could prefix its message with USR:

This system may allow for flexible communication between OpenAssistant and one
or more conversational systems.

Examples of this prefix system would need to be taught to OpenAssistant through
training data that contains such syntax. Perhaps such examples could be
generated through the work packages system.
