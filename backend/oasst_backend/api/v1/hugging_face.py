from typing import List

from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.schemas.hugging_face import ToxicityClassification
from oasst_backend.utils import get_detoxify_classification

router = APIRouter()


@router.get("/hf/text_toxicity")
def get_text_toxicity(
    msg: str,
    hf_token: str,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> List[List[ToxicityClassification]]:
    """Get the Message Toxicity from HuggingFace Roberta model.

    Args:
        msg (str): the message that we want to analyze.
        hf_token (str): the token for the huggingface access.
        api_client (ApiClient, optional): authentification of the user of the request.
            Defaults to Depends(deps.get_trusted_api_client).

    Returns:
        ToxicityClassification: the score of toxicity of the message.
    """

    return get_detoxify_classification(msg=msg, hf_token=hf_token)
