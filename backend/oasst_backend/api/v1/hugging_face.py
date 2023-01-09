from typing import List

from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.schemas.hugging_face import ToxicityClassification
from oasst_backend.utils.hugging_face import HfEmbeddingModel, HfUrl, HuggingFaceAPI

router = APIRouter()


@router.get("/text_toxicity")
async def get_text_toxicity(
    msg: str,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> List[List[ToxicityClassification]]:
    """Get the Message Toxicity from HuggingFace Roberta model.

    Args:
        msg (str): the message that we want to analyze.
        api_client (ApiClient, optional): authentification of the user of the request.
            Defaults to Depends(deps.get_trusted_api_client).

    Returns:
        ToxicityClassification: the score of toxicity of the message.
    """

    api_url: str = HfUrl.HUGGINGFACE_TOXIC_ROBERTA.value
    hugging_face_api = HuggingFaceAPI(api_url)
    response = await hugging_face_api.post(msg)

    return response


@router.get("/text_embedding")
async def get_text_embedding(
    msg: str,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> List[float]:
    """Get the Message Embedding from HuggingFace MINILM model.

    Args:
        msg (str): the message that we want to analyze.
        api_client (ApiClient, optional): authentification of the user of the request.
            Defaults to Depends(deps.get_trusted_api_client).

    Returns:
        Message Embedding (List[float]): the embedding for that message
    """

    api_url: str = HfUrl.HUGGINGFACE_FEATURE_EXTRACTION.value + "/" + HfEmbeddingModel.MINILM.value
    hugging_face_api = HuggingFaceAPI(api_url)
    response = await hugging_face_api.post(msg)

    return response
