import time
from pathlib import Path

import aiohttp
import alembic.command
import alembic.config
import fastapi
import sqlmodel
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_inference_server import auth, client_handler, deps, models, worker_handler
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.schemas import worker as worker_schema
from oasst_inference_server.settings import settings
from oasst_inference_server.user_chat_repository import UserChatRepository
from oasst_shared.schemas import inference, protocol
from prometheus_fastapi_instrumentator import Instrumentator

app = fastapi.FastAPI()


@app.middleware("http")
async def log_exceptions(request: fastapi.Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Exception in request")
        raise
    return response


# add prometheus metrics at /metrics
@app.on_event("startup")
async def enable_prom_metrics():
    Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def log_inference_protocol_version():
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")


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
                if (
                    session.exec(
                        sqlmodel.select(models.DbWorker).where(models.DbWorker.api_key == api_key)
                    ).one_or_none()
                    is None
                ):
                    logger.info(f"Adding debug API key {api_key}")
                    session.add(models.DbWorker(api_key=api_key, name="Debug API Key"))
                    session.commit()
                else:
                    logger.info(f"Debug API key {api_key} already exists")
    except Exception:
        logger.exception("Failed to add debug API keys")
        raise


@app.get("/auth/login/discord")
async def login_discord():
    redirect_uri = f"{settings.api_root}/auth/callback/discord"
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={settings.auth_discord_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@app.get("/auth/callback/discord", response_model=protocol.Token)
async def callback_discord(
    code: str,
    db: sqlmodel.Session = Depends(deps.create_session),
):
    redirect_uri = f"{settings.api_root}/auth/callback/discord"

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        # Exchange the auth code for a Discord access token
        async with session.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": settings.auth_discord_client_id,
                "client_secret": settings.auth_discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "scope": "identify",
            },
        ) as token_response:
            token_response_json = await token_response.json()

        try:
            access_token = token_response_json["access_token"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid access token response from Discord")

        # Retrieve user's Discord information using access token
        async with session.get(
            "https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}
        ) as user_response:
            user_response_json = await user_response.json()

    try:
        discord_id = user_response_json["id"]
        discord_username = user_response_json["username"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid user info response from Discord")

    # Try to find a user in our DB linked to the Discord user
    user: models.DbUser = query_user_by_provider_id(db, discord_id=discord_id)

    # Create if no user exists
    if not user:
        user = models.DbUser(provider="discord", provider_account_id=discord_id, display_name=discord_username)

        db.add(user)
        db.commit()
        db.refresh(user)

    # Discord account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token({"user_id": user.id})

    return protocol.Token(access_token=access_token, token_type="bearer")


@app.get("/chat")
async def list_chats(
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")
    chats = ucr.get_chats()
    chats_list = [chat.to_list_read() for chat in chats]
    return chats.ListChatsResponse(chats=chats_list)


@app.post("/chat")
async def create_chat(
    request: chat_schema.CreateChatRequest,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ChatListRead:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request=}")
    chat = ucr.create_chat()
    return chat.to_list_read()


@app.get("/chat/{id}")
async def get_chat(
    id: str,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ChatRead:
    """Allows a client to get the current state of a chat."""
    chat = ucr.get_chat_by_id(id)
    return chat.to_read()


app.post("/chat/{chat_id}/message")(client_handler.handle_create_message)
app.post("/chat/{chat_id}/message/{message_id}/vote")(client_handler.handle_create_vote)
app.post("/chat/{chat_id}/message/{message_id}/report")(client_handler.handle_create_report)

app.websocket("/work")(worker_handler.handle_worker)

app.on_event("startup")(worker_handler.clear_worker_sessions)
app.get("/worker_session")(worker_handler.list_worker_sessions)


@app.put("/worker")
def create_worker(
    request: worker_schema.CreateWorkerRequest,
    root_token: str = Depends(get_root_token),
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Allows a client to register a worker."""
    worker = models.DbWorker(name=request.name)
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
    workers = session.exec(sqlmodel.select(models.DbWorker)).all()
    return list(workers)


@app.delete("/worker/{worker_id}")
def delete_worker(
    worker_id: str,
    root_token: str = Depends(get_root_token),
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Deletes a worker."""
    worker = session.get(models.DbWorker, worker_id)
    session.delete(worker)
    session.commit()
    return fastapi.Response(status_code=200)


def query_user_by_provider_id(db: sqlmodel.Session, discord_id: str | None = None) -> models.DbUser | None:
    """Returns the user associated with a given provider ID if any."""
    user_qry = db.query(models.DbUser)

    if discord_id:
        user_qry = user_qry.filter(models.DbUser.provider == "discord").filter(
            models.DbUser.provider_account_id == discord_id
        )
    # elif other IDs...
    else:
        return None

    user: models.DbUser = user_qry.first()
    return user


@app.get("/auth/login/debug")
async def login_debug(username: str, db: sqlmodel.Session = Depends(deps.create_session)):
    """Login using a debug username, which the system will accept unconditionally."""

    if not settings.allow_debug_auth:
        raise HTTPException(status_code=403, detail="Debug auth is not allowed")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    # Try to find the user
    user: models.DbUser = db.exec(sqlmodel.select(models.DbUser).where(models.DbUser.id == username)).one_or_none()

    if user is None:
        logger.info(f"Creating new debug user {username=}")
        user = models.DbUser(id=username, display_name=username, provider="debug", provider_account_id=username)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Discord account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token({"user_id": user.id})

    return protocol.Token(access_token=access_token, token_type="bearer")
