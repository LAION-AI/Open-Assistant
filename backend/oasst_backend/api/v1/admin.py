import pydantic
from fastapi import APIRouter, Depends
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import Settings, settings
from oasst_backend.models.api_client import ApiClient

router = APIRouter()


class CreateApiClientRequest(pydantic.BaseModel):
    description: str
    frontend_type: str
    trusted: bool | None = False
    admin_email: str | None = None


@router.post("/api_client", response_model=str)
async def create_api_client(
    request: CreateApiClientRequest,
    root_token: str = Depends(deps.get_root_token),
    session: deps.Session = Depends(deps.get_db),
) -> str:
    logger.info(f"Creating new api client with {request=}")
    api_client = deps.create_api_client(
        session=session,
        description=request.description,
        frontend_type=request.frontend_type,
        trusted=request.trusted,
        admin_email=request.admin_email,
    )
    logger.info(f"Created api_client with key {api_client.api_key}")
    return api_client.api_key


@router.get("/backend_settings", response_model=Settings)
async def get_backend_settings(api_client: ApiClient = Depends(deps.get_trusted_api_client)) -> Settings:
    logger.info(
        f"Backend settings requested by trusted api_client {api_client.id} (admin_email: {api_client.admin_email}, frontend_type: {api_client.frontend_type})"
    )
    return settings
