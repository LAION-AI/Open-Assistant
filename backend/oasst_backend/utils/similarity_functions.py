from typing import List

import numpy as np


def cosine_similarity(a: List[float], b: List[float]):
    """Compute cosine similarity (dot product of two vectors divided by the product of their norms.)"""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        raise ZeroDivisionError("One of the vectors has a norm of zero.")
    return np.dot(a, b) / (norm_a * norm_b)


def euclidean_distance(a: List[float], b: List[float]):
    """Compute euclidean distance (norm of the difference of two vectors.)"""
    return np.linalg.norm(np.subtract(a, b))
