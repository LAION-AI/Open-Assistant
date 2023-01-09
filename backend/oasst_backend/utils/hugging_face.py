from enum import Enum
from typing import Any, Dict

import aiohttp
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.models import Message
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.exceptions import OasstError, OasstErrorCode


class HfUrl(str, Enum):
    HUGGINGFACE_TOXIC_ROBERTA = "https://api-inference.huggingface.co/models/unitary/multilingual-toxic-xlm-roberta"
    HUGGINGFACE_FEATURE_EXTRACTION = "https://api-inference.huggingface.co/pipeline/feature-extraction"


class HfModel(str, Enum):
    TOXIC_ROBERTA = "multilingual-toxic-xlm-roberta"


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
                if response.status != 200:

                    logger.error(response)
                    logger.info(self.headers)
                    raise OasstError(
                        "Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR
                    )

                # Get the response from the API call
                inference = await response.json()

        return inference


async def save_toxicity(
    interaction,
    pr: PromptRepository,
    new_message: Message,
):
    try:
        model_name = HfModel.TOXIC_ROBERTA.value
        hugging_face_api = HuggingFaceAPI(f"{HfUrl.HUGGINGFACE_TOXIC_ROBERTA.value}/{model_name}")

        toxicity = await hugging_face_api.post(interaction.text)

        toxicity_instance = pr.insert_toxicity(message_id=new_message.id, model=model_name, toxicity=toxicity)

    except OasstError:
        logger.error(
            f"Could not compute toxicity for  text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
        )

    return toxicity_instance
