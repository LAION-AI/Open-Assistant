# Retrieval Directions and Research Papers

## 1. Retrieval-Index

At first, either a rule-based search a fixed encoder for sematic vector-based
retrieval (e.g. BERT, Contriever) could be used.

### Relevant Papers

1. FAISS: [https://arxiv.org/abs/1702.08734](https://arxiv.org/abs/1702.08734) -
   vector index by Facebook
2. SCaNN: [https://arxiv.org/abs/1908.10396](https://arxiv.org/abs/1908.10396) -
   vector index by Google
3. BEIR:
   [https://arxiv.org/abs/2104.08663v4](https://arxiv.org/abs/2104.08663v4) -
   Benchmark for Information Retrieval
4. MS MARCO
   [https://arxiv.org/abs/1611.09268v3](https://arxiv.org/abs/1611.09268v3) -
   Machine Reading Comprehension Dataset / Retrieval Benchmark

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

## 2. Plugin-based approach

In this approach, the retrieval is used on top of a language model. It acts as
an additional tool, like a search engine for a human.

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

- Toolformer: [http://arxiv.org/abs/2302.04761](http://arxiv.org/abs/2302.04761)
- ...

## 3. Embedding-based approach

The embedding-based approach ingests retrieved information directly into the
model, e.g. via an additional encoder and cross-attention.

### Relevant papers

- RETRO: [http://arxiv.org/abs/2112.04426](http://arxiv.org/abs/2112.04426)
- ...
