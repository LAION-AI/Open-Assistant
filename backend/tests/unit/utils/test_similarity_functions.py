from oasst_backend.utils.similarity_functions import cos_sim, cos_sim_torch


def test_cos_sim():
    """
    Test cosine similarity
    """
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    assert cos_sim(a, b) == 0.9746318461970762


def test_cos_sim_zero():
    """
    Test cosine similarity with one of the vectors being zero
    """
    a = [1.0, 2.0, 3.0]
    b = [0.0, 0.0, 0.0]

    assert cos_sim(a, b) == 0


def test_cos_sim_torch():
    """
    Test cosine similarity
    """
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    assert cos_sim_torch(a, b) == 0.9746318461970762


def test_cos_sim_torch_zero():
    """
    Test cosine similarity with one of the vectors being zero
    """
    a = [1.0, 2.0, 3.0]
    b = [0.0, 0.0, 0.0]

    assert cos_sim_torch(a, b) == 0
