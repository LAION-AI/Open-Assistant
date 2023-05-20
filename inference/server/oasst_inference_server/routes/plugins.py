import fastapi
from oasst_inference_server import deps
from oasst_inference_server.models import DbPluginOAuthProvider
from oasst_inference_server.schemas import plugin as plugin_schema

router = fastapi.APIRouter(
    prefix="/plugins",
    tags=["plugins"],
)


async def encrypt_secret(secret: str) -> str:
    # TODO: implement
    return secret


@router.post("/oauth_provider/{provider}")
async def create_plugin_provider(
    provider: str,
    create_request: plugin_schema.CreatePluginOAuthProviderRequest,
) -> fastapi.Response:
    # TODO: outsource logic to a PluginRepository or something
    encrypted_secret = await encrypt_secret(create_request.client_secret)

    async with deps.manual_create_session() as session:
        db_provider = DbPluginOAuthProvider(
            provider=provider,
            client_id=create_request.client_id,
            client_secret=encrypted_secret,
        )

        session.add(db_provider)
        await session.commit()

    return fastapi.Response(200)
