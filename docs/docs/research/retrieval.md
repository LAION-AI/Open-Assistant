# Retrieval Directions and Research Papers

## Dataset and Benchmark

- BEIR
  [https://arxiv.org/abs/2104.08663v4](https://arxiv.org/abs/2104.08663v4) -
  Benchmark for Information Retrieval
- MS MARCO(part of BEIR)
  [https://arxiv.org/abs/1611.09268v3](https://arxiv.org/abs/1611.09268v3) -
  Machine Reading Comprehension Dataset / Retrieval Benchmark

## Search Algorithm

### Links

- ElasticSearch:
  [https://www.elastic.co/elasticsearch](https://www.elastic.co/elasticsearch)
- Apache Lucene: [https://lucene.apache.org/](https://lucene.apache.org/)
- Meta Faiss:
  [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)
- Google Scann:
  [https://github.com/google-research/google-research/tree/master/scann](https://github.com/google-research/google-research/tree/master/scann)
- Qdrant Vector DB:
  [https://github.com/qdrant/qdrant](https://github.com/qdrant/qdrant)
- Milvus Vector DB: [https://milvus.io/](https://milvus.io/)
- Open Retrieval Index Code:
  [https://github.com/kenhktsui/open-information-retrieval](https://github.com/kenhktsui/open-information-retrieval)

### Relevant Papers

- FAISS: [https://arxiv.org/abs/1702.08734](https://arxiv.org/abs/1702.08734) -
  vector index by Facebook
- SCaNN: [https://arxiv.org/abs/1908.10396](https://arxiv.org/abs/1908.10396) -
  vector index by Google

## 1. Retrieval-Index

At first, either a rule-based search or sparse vector search (e.g. BM25) or a
dense vector search (semantic search) (e.g. BERT, Contriever) could be used. In
practice, retrieval is a layered approach, where the first search is optimised
for recall and reranking is optimised for precision.

The first search in general is a sparse vector search, or dense vector search
(bi-encoder). The advantage is that it is fast because document can be
pre-indexed and stored in a DB. Cosine similarity is used to find the most
similar pre-indexed document embedding given the query embedding. Reranking is a
technique to boost the performance of top K documents from the first search. For
example, cross-encoder which takes both query and document into a language
model, and output a scalar relevance between 0 and 1. It has more superior
performance than bi-encoder because it allows interaction of query and document
in the language model. But it is slow because no index can be pre-computed.

### Links

- LangChain:
  [https://github.com/hwchase17/langchain](https://github.com/hwchase17/langchain) -
  Plugins around any language model
- LlamaIndex:
  [https://github.com/jerryjliu/llama_index](https://github.com/jerryjliu/llama_index) -
  General Retrieval System for LMs and external data
- LlamaHub: [https://llamahub.ai/](https://llamahub.ai/) - Data Source Plugins
  for LlamaIndex

### Relevant Papers

- SBERT [https://arxiv.org/abs/1908.10084](https://arxiv.org/abs/1908.10084)
- BM25+CE
  [https://arxiv.org/abs/2104.08663v4](https://arxiv.org/abs/2104.08663v4)
- RALM [https://arxiv.org/abs/2302.00083](https://arxiv.org/abs/2302.00083)
- ColBert [https://arxiv.org/abs/2004.12832](https://arxiv.org/abs/2004.12832)
- DPR [https://arxiv.org/abs/2004.04906](https://arxiv.org/abs/2004.04906)
- UPR [https://arxiv.org/abs/2204.07496](https://arxiv.org/abs/2204.07496)
- ...

## 2. Plugin-based approach

In this approach, retrieval as a tool, is embedded into the training data,
including:

- when a retrieval is required
- how to do a search (what to search)
- how to use search result As such, a language model trained with this data is
  able to do retrieval from a next token prediction objective.

### Relevant Papers

- Toolformer: [http://arxiv.org/abs/2302.04761](http://arxiv.org/abs/2302.04761)
- ...

## 3. Embedding-based approach

The embedding-based approach ingests retrieved information directly into the
model, e.g. via an additional encoder and cross-attention.

### 3a

Simply inject embeddings via cross-attention or a similar mechanism.

### 3b

Inject embeddings based on a more sophisticated architecture, e.g. make the
model decide to do retrieval and only then inject embeddings. Might be hard to
train.

### 3c

Train retrieval index jointly with the injection. Possibly infeasible as the
index needs to be re-updated during training.

### Relevant papers

- RETRO: [http://arxiv.org/abs/2112.04426](http://arxiv.org/abs/2112.04426)
- REALM: [https://arxiv.org/abs/2002.08909](https://arxiv.org/abs/2002.08909)
- RAG: [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
- Atlas [https://arxiv.org/abs/2208.03299](https://arxiv.org/abs/2208.03299)
- Unilimiformer
  [http://arxiv.org/abs/2305.01625](http://arxiv.org/abs/2305.01625)

## Paper summaries

### Borgeaud et al. 2020: Improving Language Models by Retrieving from Trillions of Tokens - "RETRO"

Idea: Use BERT (Devlin et al. 2018) as a contextual encoder for chunks of size
64 of the training data. Then train an encoder-decoder transformer model with
inputs and similar (not too similar / same) input chunks retrieved by BERT
embedding similarity - all done in a causal way (retrieve only "from the past").
The Cross-Attention is replaced by a Chunked Cross Attention optimized for
batches of similar retrieved chunks. They pre-filter their dataset such that
data duplicates cannot easily leak information via retrieval. This was scaled to
2T tokens and a 7.5 B parameter model exceeding GPT-3 performance. RETROfitting
of a pre-trained transformer also works, with small losses in perplexity (0.3),
but a lot faster training (6 % of training sequences = 6M seq à 2048 tokens).
This is not fine-tuning but just training the cross-attention, keeping
pre-trained weights fixed. Larger models benefit from more nearest neighbors,
i.e. the 7B can utilize 40 nearest neighbor chunks, a 172M model only 10 NNs.

[http://arxiv.org/abs/2112.04426](http://arxiv.org/abs/2112.04426)

### Bertsch et al. 2023: Unlimiformer: Long-Range Transformers with Unlimited Length Input

Idea: Use retrieval to actually maximize overlap of "query embeddings" with
embeddings from an encoder (in an encoder-decoder architecture). Essentially it
is an ideal approximation of the softmax in the Cross-Attention over all
previous tokens (in the encoder inputs).

Code:
[https://github.com/abertsch72/unlimiformer](https://github.com/abertsch72/unlimiformer)
Paper: [http://arxiv.org/abs/2305.01625](http://arxiv.org/abs/2305.01625)

### Izacard et al. 2022: Unsupervised Dense Information Retrieval with Contrastive Learning - "Contriver"

They present Contriver, an open-source implementation of their novel approach to
information retrieval using neural networks that outperforms traditional methods
and can be applied to a wide range of retrieval settings. The main idea behind
Contriver is to use contrastive learning to train dense retrievers for
information retrieval. Their key contribution is showing that this approach
leads to strong performance in various retrieval settings, including
cross-lingual retrieval, and outperforms traditional unsupervised term-frequency
methods such as BM25.

Specifically, on the BEIR benchmark, their unsupervised model outperforms BM25
on 11 out of 15 datasets for the Recall@100. When used as pre-training before
fine-tuning, either on a few thousands in-domain examples or on the large MS
MARCO dataset, their contrastive model leads to improvements on the BEIR
benchmark.

Pre-trained model and source code are available on Huggingface and GitHub.

### Schick et al. 2023: Toolformer: Language Models Can Teach Themselves to Use Tools

They use in-context learning of GPT-3 and some handcrafted samples to annotate a
language modeling dataset with potential uses of external tools, like QA,
wikipedia search, a calculator, machine translation and a calendar - via text
tags for those tools and respective tool queries. They use this data then to
fine-tune GPT-2/GPT-J models, implement according tools and train with up to 25k
examples per API, max sequence length 1,024. They outperform other language
models with large margin when using tools and are comparable to larger ones when
only fine-tuned on the tool-based dataset.

[http://arxiv.org/abs/2302.04761](http://arxiv.org/abs/2302.04761)

### Guu et al 2020: REALM: Retrieval-Augmented Language Model Pre-Training

They use retrieved information from a KB to train a MLM self-supervised and
evaluate on QA tasks. Predecessor to RETRO.

The authors of the paper structure the retriever in REALM such that the
computation performed for each document can be cached and asynchronously
updated, and selection of the best documents can be formulated as Maximum Inner
Product Search (MIPS). This allows for efficient retrieval of potentially
relevant documents from a large corpus during pre-training.

During pre-training, REALM backpropagates through the retrieval step that
considers millions of documents, but it does not backpropagate to each
individual document. Instead, it uses a single encoder to encode the subset of
retrieved samples and then backpropagates through this encoder. This approach
allows for efficient computation during pre-training while still allowing for
effective utilization of world knowledge.

(https://arxiv.org/abs/2002.08909)[https://arxiv.org/abs/2002.08909]

### Zamani et al. 2022: Retrieval-Enhanced Machine Learning

This paper introduces a new research program called Retrieval-Enhanced Machine
Learning (REML), which combines information retrieval techniques with machine
learning to improve model accuracy and interpretability. The authors describe
the core principles of indexing, representation, retrieval, and ranking that
underlie REML models, and provide examples of how these models have been applied
in real-world scenarios.

The main contribution of this paper is to lay out a research agenda for REML
that includes several key challenges and opportunities for future work. These
include developing new optimization algorithms that can handle large-scale data
sets, exploring the use of deep learning architectures in conjunction with
retrieval-based methods, and investigating the impact of different retrieval
strategies on model performance.

Overall, the key idea behind REML is to leverage the strengths of both
information retrieval and machine learning to create more powerful and flexible
models that can handle complex data sets and produce more accurate results. By
combining these two fields, researchers hope to pave the way for new advances in
artificial intelligence and information access research.

(https://arxiv.org/abs/2205.01230)[https://arxiv.org/abs/2205.01230]

### Thakur et al. 2021: BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

The BEIR benchmarking tool is designed to provide a comprehensive evaluation of
information retrieval models across diverse tasks and domains. It includes 18
retrieval datasets for comparison and evaluation of model generalization,
spanning nine different retrieval tasks such as fact checking, citation
prediction, duplicate question retrieval, argument retrieval, news retrieval,
question answering, tweet retrieval, bio-medical IR, and entity retrieval. The
selection methodology is motivated by the need for diverse tasks and domains to
evaluate the zero-shot capabilities of retrieval systems. The tool is
open-sourced with a standardized data format and easy-to-adapt code examples for
many different retrieval strategies.

They compare neural retrieval to legacy systems like BM25 and show that BM25 is
still a very strong baseline. The best model is a BM25 based search with
additional re-ranking based on a neural classifier.

Observations:

1. "In-domain performance is not a good indicator for out-of-domain
   generalization"
2. "Term-weighting fails, document expansion captures out-of-domain keyword
   vocabulary"
3. "Dense retrieval models with issues for out-of-distribution data"
4. "Re-ranking and Late-Interaction models generalize well to
   out-of-distribution data"
5. "Strong training losses for dense retrieval leads to better
   out-of-distribution performances"
6. "TAS-B model prefers to retrieve documents with shorter lengths"

Conclusion: Maybe not only focus on a vector-based index, use a standard index
as base + neural re-ranking

(https://arxiv.org/pdf/2104.08663.pdf)[https://arxiv.org/pdf/2104.08663.pdf]

## Other interesting papers

- Nakano et al: WebGPT (predecessor to ChatGPT) - fine-tune GPT3 to search the
  web for QA tasks
  (https://arxiv.org/pdf/2112.09332.pdf)[https://arxiv.org/pdf/2112.09332.pdf]

- Schick et al: PEER: A Collaborative Language Model
  (https://arxiv.org/pdf/2208.11663.pdf)[https://arxiv.org/pdf/2208.11663.pdf]

- Goyal et al. 2023: Retrieval Augmented Reinforcement Learning

- Humphreys et al. 2022: Large-Scale Retrieval for Reinforcement Learning
