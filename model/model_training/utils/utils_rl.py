import tritonclient.grpc as client_util
from tritonclient.utils import np_to_triton_dtype


def prepare_tensor(name: str, input):
    t = client_util.InferInput(name, input.shape, np_to_triton_dtype(input.dtype))
    t.set_data_from_numpy(input)
    return t
