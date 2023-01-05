import requests
from typing import Dict, Any


def get_detoxify_classification(inputs: Any, hf_token: str) -> Dict[Any]:

    API_URL: str = "https://api-inference.huggingface.co/models/unitary/multilingual-toxic-xlm-roberta"
    headers: Dict[str, str] = {"Authorization": f"Bearer {hf_token}"}
    payload: Dict[str, Any] = {"inputs": inputs}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()