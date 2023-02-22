import argparse

from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from exported_tree_loading import load_data
from sentence_transformers import SentenceTransformer
from similarity_functions import compute_cos_sim_kernel, embed_data, k_hop_message_passing_sparse
from sklearn.feature_extraction.text import CountVectorizer


def argument_parsing():
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--model_name", type=str, default="all-MiniLM-L6-v2")
    parser.add_argument("--cores", type=int, default=1)
    parser.add_argument("--pair_qa", type=bool, default=True)
    parser.add_argument("--use_gpu", type=bool, default=False)
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--threshold", type=float, default=0.65)
    parser.add_argument("--exported_tree_path", nargs="+", help="<Required> Set flag", required=True)
    parser.add_argument("--min_topic_size", type=int, default=10)
    parser.add_argument("--diversity", type=float, default=0.2)
    parser.add_argument("--reduce_frequent_words", type=bool, default=False)
    parser.add_argument("--reduce_outliers_strategy", type=str, default="c-tf-idf")

    args = parser.parse_args()
    return args


def load_topic_model(args):
    vectorizer_model = CountVectorizer(stop_words="english")
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
    model = SentenceTransformer(MODEL_NAME)
    representation_model = MaximalMarginalRelevance(diversity=args.diversity)
    topic_model = BERTopic(
        nr_topics="auto",
        min_topic_size=args.min_topic_size,
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
    return topic_model.get_representative_docs()


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


def compute_hierarchical_topic_tree(topic_model, data, key="query"):
    hierarchical_topics = topic_model.hierarchical_topics(data[key].to_list())
    tree = topic_model.get_topic_tree(hierarchical_topics)
    return hierarchical_topics, tree


if __name__ == "__main__":
    """
    Main function to run topic modeling on a list of exported message trees.
    Example usage:
    python message_tree_topic_modeling.py --exported_tree_path 2023-02-06_oasst_prod.jsonl 2023-02-07_oasst_prod.jsonl
    """
    args = argument_parsing()
    MODEL_NAME = args.model_name
    data, message_list = load_data(args.exported_tree_path, args.pair_qa)
    embs = embed_data(data, model_name=MODEL_NAME, cores=args.cores, gpu=args.use_gpu)
    adj_matrix = compute_cos_sim_kernel(embs, args.threshold)
    print(adj_matrix.shape)
    print(embs.shape)
    A_k, agg_features = k_hop_message_passing_sparse(adj_matrix, embs, args.k)
    print(A_k.shape)
    topic_model = load_topic_model(args)
    topics, probs = fit_topic_model(topic_model, data, agg_features)
    freq = get_topic_info(topic_model)
    rep_docs = get_representative_docs(topic_model)
    print(freq)
    for k, v in rep_docs.items():
        print(k)
        print(v)
        print("\n\n\n")
