from typing import Any, Dict

import requests
from oasst_backend.constants import HUGGINGFACE_TOXIC_ROBERTA_URL
from oasst_shared.exceptions import OasstError, OasstErrorCode


def get_detoxify_classification(inputs: Any, hf_token: str) -> Dict[Any]:
    headers: Dict[str, str] = {"Authorization": f"Bearer {hf_token}"}
    payload: Dict[str, Any] = {"inputs": inputs}
    response = requests.post(HUGGINGFACE_TOXIC_ROBERTA_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

    return response.json()
