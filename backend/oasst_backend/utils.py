from typing import Dict, List

import requests
from oasst_backend.config import settings
from oasst_backend.constants import HUGGINGFACE_TOXIC_ROBERTA_URL
from oasst_backend.schemas.hugging_face import ToxicityClassification
from oasst_shared.exceptions import OasstError, OasstErrorCode
from requests.models import Response


def get_detoxify_classification(msg: str) -> List[List[ToxicityClassification]]:
    """Classification of a msg by the HuggingFace model of Roberta.

    Args:
        msg (str): the message we want to classify

    Raises:
        OasstError: error in the response from the API

    Returns:
        ToxicityClassification: classification of the message
    """
    headers: Dict[str, str] = {"Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}"}
    payload: Dict[str, str] = {"inputs": msg}
    response: Response = requests.post(HUGGINGFACE_TOXIC_ROBERTA_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

    return response.json()


if __name__ == "__main__":
    res = get_detoxify_classification("Bullshit", "")

    print(res)
