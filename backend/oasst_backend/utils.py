from typing import Any, Dict, List

import requests
from oasst_backend.constants import HUGGINGFACE_TOXIC_ROBERTA_URL
from oasst_backend.schemas.hugging_face import ToxicityClassification
from oasst_shared.exceptions import OasstError, OasstErrorCode
from requests.models import Response


def get_detoxify_classification(msg: str, hf_token: str) -> List[List[ToxicityClassification]]:
    """Classification of a msg by the HuggingFace model of Roberta.

    Args:
        msg (str): the message we want to classify
        hf_token (str): api key to use the API endpoint of HuggingFace

    Raises:
        OasstError: error in the response from the API

    Returns:
        Dict[str, Any]: _description_
    """
    headers: Dict[str, str] = {"Authorization": f"Bearer {hf_token}"}
    payload: Dict[str, Any] = {"inputs": msg}
    response: Response = requests.post(HUGGINGFACE_TOXIC_ROBERTA_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

    return response.json()


if __name__ == "__main__":
    res = get_detoxify_classification("Bullshit", "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")

    print(res)
