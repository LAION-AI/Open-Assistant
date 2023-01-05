from typing import Any, Dict

import requests
from constants import HUGGINGFACE_TOXIC_ROBERTA_URL
from oasst_shared.exceptions import OasstError, OasstErrorCode
from requests.models import Response


def get_detoxify_classification(msg: str, hf_token: str) -> Dict[str, Any]:
    headers: Dict[str, str] = {"Authorization": f"Bearer {hf_token}"}
    payload: Dict[str, Any] = {"inputs": msg}
    response: Response = requests.post(HUGGINGFACE_TOXIC_ROBERTA_URL, headers=headers, json=payload)
    print(response)

    if response.status_code != 200:
        raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

    return response.json()


if __name__ == "__main__":
    res = get_detoxify_classification("Bullshit", "")

    print(res)
