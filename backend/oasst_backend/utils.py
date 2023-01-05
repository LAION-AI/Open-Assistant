import requests
from typing import Dict, Any
from oasst_backend.constants import HUGGINGFACE_TOXIC_ROBERTA_URL


def get_detoxify_classification(inputs: Any, hf_token: str) -> Dict[Any]:
    headers: Dict[str, str] = {"Authorization": f"Bearer {hf_token}"}
    payload: Dict[str, Any] = {"inputs": inputs}
    response = requests.post(HUGGINGFACE_TOXIC_ROBERTA_URL, headers=headers, json=payload)
    return response.json()