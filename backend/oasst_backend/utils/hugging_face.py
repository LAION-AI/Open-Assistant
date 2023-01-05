from typing import Dict, List

import aiohttp
from oasst_backend.config import settings
from oasst_backend.schemas.hugging_face import ToxicityClassification
from oasst_shared.exceptions import OasstError, OasstErrorCode


class HuggingFaceAPI:
    def __init__(
        self,
        api_url: str,
    ):

        self.api_url: str = api_url
        self.api_key: str = settings.HUGGING_FACE_API_KEY
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {self.api_key}"}

    # @classmethod TODO
    async def post(self, input: str) -> List[List[ToxicityClassification]]:

        payload: Dict[str, str] = {"inputs": input}
        session = aiohttp.ClientSession()
        response = await session.post(self.api_url, headers=self.headers, json=payload)

        if response.status != 200:
            raise OasstError("Response Error Detoxify HuggingFace", error_code=OasstErrorCode.HUGGINGFACE_API_ERROR)

        return await response.json()
