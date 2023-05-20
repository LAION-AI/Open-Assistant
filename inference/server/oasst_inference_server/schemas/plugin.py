import pydantic


class CreateOAuthProviderRequest(pydantic.BaseModel):
    client_id: str
    client_secret: str


class CreateOAuthProviderResponse(pydantic.BaseModel):
    verification_token: str
