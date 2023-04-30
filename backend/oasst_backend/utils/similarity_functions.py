import math

import numpy as np
import scipy.sparse as sp
import torch
import torch.nn.functional as F
from pandas import DataFrame
from sentence_transformers import SentenceTransformer
from torch import Tensor
from tqdm import tqdm

ADJACENCY_THRESHOLD = 0.65


def embed_data(
    data: DataFrame,
    key: str = "query",
    model_name: str = "all-MiniLM-L6-v2",
    cores: int = 1,
    gpu: bool = False,
    batch_size: int = 128,
):
    """
    Embed the sentences/text using the MiniLM language model (which uses mean pooling)
    """
    print("Embedding data")
    model = SentenceTransformer(model_name)
    print("Model loaded")

    sentences = data[key].tolist()
    unique_sentences = data[key].unique()
    print("Unique sentences", len(unique_sentences))

    if cores == 1:
        embeddings = model.encode(unique_sentences, show_progress_bar=True, batch_size=batch_size)
    else:
        devices = ["cpu"] * cores
        if gpu:
            devices = None  # use all CUDA devices

        # Start the multi-process pool on multiple devices
        print("Multi-process pool starting")
        pool = model.start_multi_process_pool(devices)
        print("Multi-process pool started")

        chunk_size = math.ceil(len(unique_sentences) / cores)

        # Compute the embeddings using the multi-process pool
        embeddings = model.encode_multi_process(unique_sentences, pool, batch_size=batch_size, chunk_size=chunk_size)
        model.stop_multi_process_pool(pool)

    print("Embeddings computed")

    mapping = {sentence: embedding for sentence, embedding in zip(unique_sentences, embeddings)}
    embeddings = np.array([mapping[sentence] for sentence in sentences])

    return embeddings


def cos_sim(a: Tensor, b: Tensor):
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not isinstance(a, torch.Tensor):
        a = torch.tensor(np.array(a))

    if not isinstance(b, torch.Tensor):
        b = torch.tensor(np.array(b))

    if len(a.shape) == 1:
        a = a.unsqueeze(0)

    if len(b.shape) == 1:
        b = b.unsqueeze(0)

    a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
    b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
    return torch.mm(a_norm, b_norm.transpose(0, 1))


def cos_sim_torch(embs_a: Tensor, embs_b: Tensor) -> Tensor:
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    Using torch.nn.functional.cosine_similarity
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not isinstance(embs_a, torch.Tensor):
        embs_a = torch.tensor(np.array(embs_a))

    if not isinstance(embs_b, torch.Tensor):
        embs_b = torch.tensor(np.array(embs_b))

    if len(embs_a.shape) == 1:
        embs_a = embs_a.unsqueeze(0)

    if len(embs_b.shape) == 1:
        embs_b = embs_b.unsqueeze(0)
    A = F.cosine_similarity(embs_a.unsqueeze(1), embs_b.unsqueeze(0), dim=2)
    return A


def gaussian_kernel_torch(embs_a, embs_b, sigma=1.0):
    """
    Computes the Gaussian kernel matrix between two sets of embeddings using PyTorch.
    :param embs_a: Tensor of shape (batch_size_a, embedding_dim) containing the first set of embeddings.
    :param embs_b: Tensor of shape (batch_size_b, embedding_dim) containing the second set of embeddings.
    :param sigma: Width of the Gaussian kernel.
    :return: Tensor of shape (batch_size_a, batch_size_b) containing the Gaussian kernel matrix.
    """
    if not isinstance(embs_a, torch.Tensor):
        embs_a = torch.tensor(embs_a)

    if not isinstance(embs_b, torch.Tensor):
        embs_b = torch.tensor(embs_b)

    # Compute the pairwise distances between the embeddings
    dist_matrix = torch.cdist(embs_a, embs_b)

    # Compute the Gaussian kernel matrix
    kernel_matrix = torch.exp(-(dist_matrix**2) / (2 * sigma**2))

    return kernel_matrix


def compute_cos_sim_kernel(embs, threshold=0.65, kernel_type="cosine"):
    # match case to kernel type
    if kernel_type == "gaussian":
        A = gaussian_kernel_torch(embs, embs)
    if kernel_type == "cosine":
        A = cos_sim_torch(embs, embs)
    adj_matrix = torch.zeros_like(A)
    adj_matrix[A > threshold] = 1
    adj_matrix[A <= threshold] = 0
    adj_matrix = adj_matrix.numpy().astype(np.float32)
    return adj_matrix


def k_hop_message_passing(A, node_features, k):
    """
    Compute the k-hop adjacency matrix and aggregated features using message passing.

    Parameters:
    A (numpy array): The adjacency matrix of the graph.
    node_features (numpy array): The feature matrix of the nodes.
    k (int): The number of hops for message passing.

    Returns:
    A_k (numpy array): The k-hop adjacency matrix.
    agg_features (numpy array): The aggregated feature matrix for each node in the k-hop neighborhood.
    """

    print("Compute the k-hop adjacency matrix")
    A_k = np.linalg.matrix_power(A, k)

    print("Aggregate the messages from the k-hop neighborhood:")
    agg_features = node_features.copy()

    for i in tqdm(range(k)):
        agg_features += np.matmul(np.linalg.matrix_power(A, i + 1), node_features)

    return A_k, agg_features


def k_hop_message_passing_sparse(A, node_features, k):
    """
    Compute the k-hop adjacency matrix and aggregated features using message passing.

    Parameters:
    A (numpy array or scipy sparse matrix): The adjacency matrix of the graph.
    node_features (numpy array or scipy sparse matrix): The feature matrix of the nodes.
    k (int): The number of hops for message passing.

    Returns:
    A_k (numpy array): The k-hop adjacency matrix.
    agg_features (numpy array): The aggregated feature matrix for each node in the k-hop neighborhood.
    """

    # Convert input matrices to sparse matrices if they are not already
    if not sp.issparse(A):
        A = sp.csr_matrix(A)
    if not sp.issparse(node_features):
        node_features = sp.csr_matrix(node_features)

    # Compute the k-hop adjacency matrix and the aggregated features
    A_k = A.copy()
    agg_features = node_features.copy()

    for i in tqdm(range(k)):
        # Compute the message passing for the k-hop neighborhood
        message = A_k.dot(node_features)
        # Apply a GCN layer to aggregate the messages
        agg_features = A_k.dot(agg_features) + message
        # Update the k-hop adjacency matrix by adding new edges
        A_k += A_k.dot(A)

    return A_k.toarray(), agg_features.toarray()
