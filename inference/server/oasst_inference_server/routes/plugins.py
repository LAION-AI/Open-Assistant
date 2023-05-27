import json
import uuid

import aiohttp
import fastapi
import sqlmodel
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from jose import jwe
from oasst_inference_server import database, deps, models
from oasst_inference_server.schemas import plugin as plugin_schema
from oasst_inference_server.settings import settings

router = fastapi.APIRouter(
    prefix="/plugins",
    tags=["plugins"],
)


def derive_plugin_key() -> bytes:
    """Derive a key from the plugin auth secret."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=settings.plugin_auth_length,
        salt=settings.plugin_auth_salt,
        info=settings.plugin_auth_info,
    )
    key = hkdf.derive(settings.plugin_auth_secret)
    return key


def encrypt_secret(secret: str) -> str:
    payload = json.dumps({"secret": secret}).encode()
    key = derive_plugin_key()
    encrypted: bytes = jwe.encrypt(payload, key)
    return encrypted.decode()


def decrypt_secret(encrypted_secret: str) -> str:
    key = derive_plugin_key()
    decrypted = jwe.decrypt(encrypted_secret, key)
    payload: dict = json.loads(decrypted.decode())
    secret = payload["secret"]
    return secret


def generate_verification_token() -> str:
    # TODO: check how verification tokens should be generated and possibly replace this
    # TODO: possibly store this in DB
    return uuid.uuid4()


async def get_provider(session: database.AsyncSession, provider: str) -> models.DbPluginOAuthProvider:
    qry = sqlmodel.select(models.DbPluginOAuthProvider).filter(
        models.DbPluginOAuthProvider.provider == provider,
    )
    db_provider: models.DbPluginOAuthProvider = (await session.exec(qry)).one_or_none()
    if not db_provider:
        raise fastapi.HTTPException(status_code=404)
    return db_provider


def prepare_request_content(content_type: str, data: dict):
    if content_type == "application/json":
        return json.dumps(data)
    # TODO: support other content types
    return json.dumps(data)


async def get_auth_response(
    auth_url: str, content_type: str, client_id: str, client_secret: str, code: str, redirect_uri: str
) -> dict:
    data_dict = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    headers = {
        "Content-Type": content_type,
    }

    request_content = prepare_request_content(content_type, data_dict)

    async with aiohttp.ClientSession(raise_for_status=True) as http_session:
        async with http_session.post(auth_url, headers=headers, data=request_content) as response:
            response_json = await response.json()

    return response_json


@router.post("/oauth_provider/{provider}", response_model=plugin_schema.CreateOAuthProviderResponse)
async def create_provider(
    provider: str,
    create_request: plugin_schema.CreateOAuthProviderRequest,
) -> plugin_schema.CreateOAuthProviderResponse:
    # TODO: outsource logic to a PluginRepository or something
    encrypted_secret = encrypt_secret(create_request.client_secret)

    async with deps.manual_create_session() as session:
        db_provider = models.DbPluginOAuthProvider(
            provider=provider,
            client_id=create_request.client_id,
            client_secret=encrypted_secret,
        )

        session.add(db_provider)
        await session.commit()

    token = generate_verification_token()

    return plugin_schema.CreateOAuthProviderResponse(
        verification_token=token,
    )


@router.get("/oauth_provider/{provider}/login")
async def login_plugin(provider: str):
    async with deps.manual_create_session() as db_session:
        db_provider: models.DbPluginOAuthProvider = get_provider(db_session, provider)

    redirect_uri = f"{settings.api_root}/plugins/oauth_provider/{provider}/callback"

    # TODO: plugin specific, how do we get them
    target_url_base = ""
    scope: str = ""

    target_url = f"{target_url_base}?response_type=code&client_id={db_provider.client_id}&redirect_uri={redirect_uri}&scope={scope}"

    raise fastapi.HTTPException(status_code=302, headers={"location": target_url})


@router.get("/oauth_provider/{provider}/callback")
async def callback_plugin(provider: str, code: str):
    async with deps.manual_create_session() as db_session:
        db_provider: models.DbPluginOAuthProvider = get_provider(db_session, provider)

    # TODO: auth_url and content_type come from ai-plugin.json, but we don't have an easy way to grab here
    auth_url: str = ""
    content_type: str = "application/json"
    client_secret: str = decrypt_secret(db_provider.client_secret)
    code: str = ""
    redirect_uri: str = f"{settings.api_root}/plugins/oauth_provider/{provider}/callback"

    auth_response: dict = get_auth_response(
        auth_url, content_type, db_provider.client_id, client_secret, code, redirect_uri
    )

    auth_response
    # TODO
