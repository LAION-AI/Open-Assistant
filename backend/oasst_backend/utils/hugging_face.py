from enum import Enum
from typing import Any, Dict

import aiohttp
from loguru import logger
from oasst_backend.config import settings
from oasst_shared.exceptions import OasstError, OasstErrorCode


class HfUrl(str, Enum):
    HUGGINGFACE_TOXIC_CLASSIFICATION = "https://api-inference.huggingface.co/models"
    HUGGINGFACE_FEATURE_EXTRACTION = "https://api-inference.huggingface.co/pipeline/feature-extraction"


class HfClassificationModel(str, Enum):
    TOXIC_ROBERTA = "unitary/multilingual-toxic-xlm-roberta"


class HfEmbeddingModel(str, Enum):
    MINILM = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class HuggingFaceAPI:
    """Class Object to make post calls to endpoints for inference in models hosted in HuggingFace"""

    def __init__(
        self,
        api_url: str,
    ):
        # The API endpoint we want to access
        self.api_url: str = api_url

        # Access token for the api
        self.api_key: str = settings.HUGGING_FACE_API_KEY

        # Headers going to be used
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {self.api_key}"}

    async def post(self, input: str) -> Any:
        """Post request to the endpoint to get an inference

        Args:
            input (str): the input that we will pass to the model

        Raises:
            OasstError: in the case we get a bad response

        Returns:
            inference: the inference we obtain from the model in HF
        """

        async with aiohttp.ClientSession() as session:
            payload: Dict[str, str] = {"inputs": input}

            async with session.post(self.api_url, headers=self.headers, json=payload) as response:
                # If we get a bad response
                if not response.ok:
                    logger.error(response)
                    logger.info(self.headers)
                    raise OasstError(
                        f"Response Error HuggingFace API (Status: {response.status})",
                        error_code=OasstErrorCode.HUGGINGFACE_API_ERROR,
                    )

                # Get the response from the API call
                inference = await response.json()

        return inference
