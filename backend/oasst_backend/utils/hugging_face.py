from typing import Any, Dict

import aiohttp
from oasst_backend.config import settings
from oasst_shared.exceptions import OasstError, OasstErrorCode


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
                    raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

                # Get the response from the API call
                inference = await response.json()

        return inference
