import pydantic


class CreatePluginOAuthProviderRequest(pydantic.BaseModel):
    client_id: str
    client_secret: str
