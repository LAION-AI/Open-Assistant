from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from exported_tree_loading import load_data
from sentence_transformers import SentenceTransformer
from similarity_functions import compute_cos_sim_kernel, embed_data, k_hop_message_passing_sparse
from sklearn.feature_extraction.text import CountVectorizer

MODEL_NAME = "all-MiniLM-L6-v2"


def load_topic_model():
    vectorizer_model = CountVectorizer(stop_words="english")
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
    model = SentenceTransformer(MODEL_NAME)
    representation_model = MaximalMarginalRelevance(diversity=0.2)
    topic_model = BERTopic(
        nr_topics="auto",
        min_topic_size=10,
        representation_model=representation_model,
        vectorizer_model=vectorizer_model,
        ctfidf_model=ctfidf_model,
        embedding_model=model,
    )
    return topic_model


def fit_topic_model(topic_model, data, embeddings, key="query"):
    topics, probs = topic_model.fit_transform(data[key].to_list(), embeddings)
    return topics, probs


def get_topic_info(topic_model):
    return topic_model.get_topic_info()


def reduce_topics(topic_model, data, nr_topics, key="query"):
    topic_model.reduce_topics(data[key].to_list(), nr_topics)
    return topic_model


def get_representative_docs(topic_model):
    return topic_model.get_representative_documents()


def reduce_outliers(topic_model, data, topics, probs, key="query", strategy="c-tf-idf"):
    if strategy == "c-tf-idf":
        new_topics = topic_model.reduce_outliers(data[key].to_list(), topics, strategy, threshold=0.1)
    elif strategy == "embeddings":
        new_topics = topic_model.reduce_outliers(data[key].to_list(), topics, strategy)
    elif strategy == "distributions":
        new_topics = topic_model.reduce_outliers(data[key].to_list(), topics, probabilities=probs, strategy=strategy)
    else:
        raise ValueError("Invalid strategy")
    return new_topics


def compute_heirarchical_topic_tree(topic_model, data, key="query"):
    hierarchical_topics = topic_model.hierarchical_topics(data[key].to_list())
    tree = topic_model.get_topic_tree(hierarchical_topics)
    return hierarchical_topics, tree


if __name__ == "__main__":
    data, message_list = load_data(["./2023-02-06_oasst_prod.jsonl"])
    embs = embed_data(data, model_name=MODEL_NAME, cores=1, gpu=False)
    adj_matrix = compute_cos_sim_kernel(embs)
    print(adj_matrix.shape)
    print(embs.shape)
    A_k, agg_features = k_hop_message_passing_sparse(adj_matrix, embs, 2)
    print(A_k.shape)
    topic_model = load_topic_model()
    topics, probs = fit_topic_model(topic_model, data, agg_features)
    freq = get_topic_info(topic_model)
    rep_docs = get_representative_docs(topic_model)
    print(freq)
    print(rep_docs)
