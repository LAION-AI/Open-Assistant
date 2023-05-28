import pydantic


class CreateOAuthProviderRequest(pydantic.BaseModel):
    plugin_config_url: str
    client_id: str
    client_secret: str


class CreateOAuthProviderResponse(pydantic.BaseModel):
    verification_token: str


class PluginOAuthResponse(pydantic.BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
