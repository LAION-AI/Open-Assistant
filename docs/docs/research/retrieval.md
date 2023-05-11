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
pre-indexed and stored in a DB. Consine similarity is used to find the most
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

### Relevant papers

- RETRO: [http://arxiv.org/abs/2112.04426](http://arxiv.org/abs/2112.04426)
- REALM: [https://arxiv.org/abs/2002.08909](https://arxiv.org/abs/2002.08909)
- RAG: [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
- Atlas [https://arxiv.org/abs/2208.03299](https://arxiv.org/abs/2208.03299)
- ...
