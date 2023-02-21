import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import alembic.command
import alembic.config
import fastapi
import sqlmodel
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie
from fastapi_discord import DiscordOAuthClient
from fastapi_discord.models import User as DiscordUser
from jose import jwe, jwt
from loguru import logger
from oasst_inference_server import client_handler, deps, interface, worker_handler
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.models import DbUser, DbWorker
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference, protocol
from prometheus_fastapi_instrumentator import Instrumentator

app = fastapi.FastAPI()
oauth2_scheme = APIKeyCookie(name=settings.AUTH_COOKIE_NAME)
discord = DiscordOAuthClient(
    settings.auth_discord_client_id, settings.auth_discord_client_secret, "/auth/callback/discord/", ("identify",)
)


# add prometheus metrics at /metrics
@app.on_event("startup")
async def enable_prom_metrics():
    Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def log_inference_protocol_version():
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")


@app.on_event("startup")
async def init_discord_oauth():
    await discord.init()


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_bearer_token(authorization_header: str) -> str:
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must start with 'Bearer '")
    return authorization_header[len("Bearer ") :]


def get_root_token(token: str = Depends(get_bearer_token)) -> str:
    root_token = settings.root_token
    if token == root_token:
        return token
    raise HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@app.on_event("startup")
def alembic_upgrade():
    if not settings.update_alembic:
        logger.info("Skipping alembic upgrade on startup (update_alembic is False)")
        return
    logger.info("Attempting to upgrade alembic on startup")
    retry = 0
    while True:
        try:
            alembic_ini_path = Path(__file__).parent / "alembic.ini"
            alembic_cfg = alembic.config.Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_uri)
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("Successfully upgraded alembic on startup")
            break
        except Exception:
            logger.exception("Alembic upgrade failed on startup")
            retry += 1
            if retry >= settings.alembic_retries:
                raise

            timeout = settings.alembic_retry_timeout * 2**retry
            logger.warning(f"Retrying alembic upgrade in {timeout} seconds")
            time.sleep(timeout)


@app.on_event("startup")
def maybe_add_debug_api_keys():
    if not settings.debug_api_keys:
        logger.info("No debug API keys configured, skipping")
        return
    try:
        logger.info("Adding debug API keys")
        with deps.manual_create_session() as session:
            for api_key in settings.debug_api_keys:
                logger.info(f"Checking if debug API key {api_key} exists")
                if session.exec(sqlmodel.select(DbWorker).where(DbWorker.api_key == api_key)).one_or_none() is None:
                    logger.info(f"Adding debug API key {api_key}")
                    session.add(DbWorker(api_key=api_key, name="Debug API Key"))
                    session.commit()
                else:
                    logger.info(f"Debug API key {api_key} already exists")
    except Exception:
        logger.exception("Failed to add debug API keys")
        raise


@app.get("/auth/login/discord")
async def login_discord():
    # Provide Discord OAuth login URL, which will redirect to our callback after login
    return {"url": discord.oauth_login_url}


@app.get("/auth/callback/discord", response_model=protocol.Token)
async def callback_discord(
    code: str,
    db: sqlmodel.Session = Depends(deps.create_session),
):
    # Exchange code for access token with Discord
    token, _ = await discord.get_access_token(code)

    # Get user info from Discord using Discord access token
    discord_user: DiscordUser = DiscordUser(**(await discord.request("/users/@me", token)))

    # Get user in our DB linked to the Discord user, creating if not exists
    user: DbUser = get_user_from_discord_id(db, discord_user.id, create_if_not_exists=True)

    # Discord account is authenticated and linked to a user; create JWT
    access_token = create_access_token(
        {"user_id": user.id},
        settings.auth_secret,
        settings.auth_algorithm,
        settings.auth_access_token_expire_minutes,
    )

    return protocol.Token(access_token=access_token, token_type="bearer")


@app.get("/chat")
async def list_chats(cr: ChatRepository = Depends(deps.create_chat_repository)) -> interface.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")
    chats = cr.get_chat_list()
    return interface.ListChatsResponse(chats=chats)


@app.post("/chat")
async def create_chat(
    request: interface.CreateChatRequest, cr: ChatRepository = Depends(deps.create_chat_repository)
) -> interface.ChatListRead:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request=}")
    chat = cr.create_chat()
    return chat.to_list_read()


@app.get("/chat/{id}")
async def get_chat(id: str, cr: ChatRepository = Depends(deps.create_chat_repository)) -> interface.ChatRead:
    """Allows a client to get the current state of a chat."""
    chat = cr.get_chat_by_id(id)
    return chat.to_read()


app.post("/chat/{chat_id}/message")(client_handler.handle_create_message)

app.websocket("/work")(worker_handler.handle_worker)

app.on_event("startup")(worker_handler.clear_worker_sessions)
app.get("/worker_session")(worker_handler.list_worker_sessions)


@app.put("/worker")
def create_worker(
    request: interface.CreateWorkerRequest,
    root_token: str = Depends(get_root_token),
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Allows a client to register a worker."""
    worker = DbWorker(
        name=request.name,
    )
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


@app.get("/worker")
def list_workers(
    root_token: str = Depends(get_root_token),
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Lists all workers."""
    workers = session.exec(sqlmodel.select(DbWorker)).all()
    return list(workers)


@app.delete("/worker/{worker_id}")
def delete_worker(
    worker_id: str,
    root_token: str = Depends(get_root_token),
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Deletes a worker."""
    worker = session.get(DbWorker, worker_id)
    session.delete(worker)
    session.commit()
    return fastapi.Response(status_code=200)


def get_user_from_discord_id(
    db: sqlmodel.Session, discord_id: str, create_if_not_exists: bool = False
) -> Optional[DbUser]:
    """Returns the user associated with the given Discord ID if any."""
    user: DbUser = (
        db.query(DbUser).filter(DbUser.provider_account_id == discord_id).filter(DbUser.provider == "discord").first()
    )

    if not user and create_if_not_exists:
        user = DbUser(
            provider="discord",
            provider_account_id=discord_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def create_access_token(data: dict, secret: str, algorithm: str, expire_minutes: int) -> str:
    """Create encoded JSON Web Token (JWT) using the given data."""
    expires_delta = timedelta(minutes=expire_minutes)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


def decode_access_token(token: str = Security(oauth2_scheme)) -> dict:
    """Decode the current user JWT token and return the payload."""
    # We first generate a key from the auth secret
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=settings.AUTH_LENGTH,
        salt=settings.AUTH_SALT,
        info=settings.AUTH_INFO,
    )
    key = hkdf.derive(settings.auth_secret)
    # Next we decrypt the JWE token
    payload = jwe.decrypt(token, key)
    # This JSON payload will have "user_id" and "exp" keys
    return payload
