import json
from base64 import b64decode

import pydantic
from pydantic import validator


class TrustedClient(pydantic.BaseModel):
    api_key: str
    client: str  # "website", "discord", or similar
    user_id: str  # the id of the user in the data backend
    provider_account_id: str  # id of the user in the client
    username: str


class TrustedClientToken(pydantic.BaseModel):
    content: TrustedClient

    @validator("content", pre=True)
    def parse(token: str):
        return json.loads(b64decode(token))
