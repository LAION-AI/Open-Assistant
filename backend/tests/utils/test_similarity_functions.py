import pytest
from oasst_backend.utils.similarity_functions import cosine_similarity, euclidean_distance


def test_cosine_similarity():
    """
    Test cosine similarity
    """
    a = [1, 2, 3]
    b = [4, 5, 6]
    assert cosine_similarity(a, b) == 0.9746318461970762


def test_cosine_similarity_zero():
    """
    Test cosine similarity with one of the vectors being zero
    """
    a = [1, 2, 3]
    b = [0, 0, 0]

    with pytest.raises(ZeroDivisionError):
        cosine_similarity(a, b)


def test_euclidean_distance():
    """
    Test euclidean distance
    """
    a = [1, 2, 3]
    b = [4, 5, 6]
    assert euclidean_distance(a, b) == 5.196152422706632
