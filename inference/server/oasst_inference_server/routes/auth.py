import fastapi
import sqlmodel
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException, Request, Security
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger
from oasst_inference_server import auth, database, deps, models
from oasst_inference_server.schemas.auth import TrustedClient, TrustedClientToken
from oasst_inference_server.settings import settings
from oasst_shared.schemas import protocol

router = fastapi.APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth = OAuth()
oauth_providers: list[str] = []


@router.on_event("startup")
def register_oauth_providers():
    if settings.auth_discord_client_id:
        oauth.register(
            name="discord",
            client_id=settings.auth_discord_client_id,
            client_secret=settings.auth_discord_client_secret,
            access_token_url="https://discord.com/api/oauth2/token",
            authorize_url="https://discord.com/api/oauth2/authorize",
            api_base_url="https://discord.com/api/",
            client_kwargs={"scope": "identify"},
        )

        oauth_providers.append("discord")

    if settings.auth_github_client_id:
        oauth.register(
            name="github",
            client_id=settings.auth_github_client_id,
            client_secret=settings.auth_github_client_secret,
            access_token_url="https://github.com/login/oauth/access_token",
            authorize_url="https://github.com/login/oauth/authorize",
            api_base_url="https://api.github.com/",
            client_kwargs={"scope": "read:user"},
        )

        oauth_providers.append("github")

    if settings.auth_google_client_id:
        oauth.register(
            name="google",
            client_id=settings.auth_google_client_id,
            client_secret=settings.auth_google_client_secret,
            access_token_url="https://accounts.google.com/o/oauth2/token",
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            api_base_url="https://www.googleapis.com/oauth2/v1/",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile"},
        )

        oauth_providers.append("google")

    if settings.allow_debug_auth:
        oauth_providers.append("debug")


@router.get("/check")
async def check_user_auth(user_id: str = Depends(auth.get_current_user_id)):
    return user_id


@router.get("/providers")
async def get_available_auth_providers():
    if len(oauth_providers) == 0:
        logger.warn("No login providers available, logging in is not possible.")
    return oauth_providers


@router.get("/refresh", response_model=protocol.Token)
async def refresh_token(refresh_token: str = Security(auth.refresh_scheme)):
    access_token = await auth.refresh_access_token(refresh_token)
    return protocol.Token(access_token=access_token, token_type="bearer")


@router.get("/login/discord")
async def login_discord(request: Request):
    redirect_uri = f"{settings.api_root}/auth/callback/discord"
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback/discord", response_model=protocol.TokenPair)
async def callback_discord(
    request: Request,
    db: database.AsyncSession = Depends(deps.create_session),
):
    token = await oauth.discord.authorize_access_token(request)
    user_response = await oauth.discord.get("users/@me", token=token)

    user_response_json = user_response.json()

    try:
        discord_id = user_response_json["id"]
        discord_username = user_response_json["username"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid user info response from Discord")

    user: models.DbUser = await get_or_create_user(db, "discord", discord_id, discord_username)
    token_pair: protocol.TokenPair = await create_tokens(user)
    return token_pair


@router.get("/login/github")
async def login_github(request: Request):
    redirect_uri = f"{settings.api_root}/auth/callback/github"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/callback/github", response_model=protocol.TokenPair)
async def callback_github(
    request: Request,
    db: database.AsyncSession = Depends(deps.create_session),
):
    token = await oauth.github.authorize_access_token(request)
    user_response = await oauth.github.get("user", token=token)

    user_response_json = user_response.json()

    try:
        github_id = str(user_response_json["id"])
        github_username = user_response_json["login"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid user info response from GitHub")

    user: models.DbUser = await get_or_create_user(db, "github", github_id, github_username)
    token_pair: protocol.TokenPair = await create_tokens(user)
    return token_pair


@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = f"{settings.api_root}/auth/callback/google"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback/google", response_model=protocol.TokenPair)
async def callback_google(
    request: Request,
    db: database.AsyncSession = Depends(deps.create_session),
):
    token = await oauth.google.authorize_access_token(request)
    credentials = Credentials.from_authorized_user_info(token)

    people_api = build("people", "v1", credentials=credentials)
    profile = people_api.people().get(resourceName="people/me", personFields="names").execute()

    try:
        google_id = profile["resourceName"].split("/")[1]
        google_username = profile["names"][0]["displayName"] if len(profile["names"]) > 0 else "User"
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid user info response from Google")

    user: models.DbUser = await get_or_create_user(db, "google", google_id, google_username)
    token_pair: protocol.TokenPair = await create_tokens(user)
    return token_pair


async def get_or_create_user(
    db: database.AsyncSession, provider: str, provider_id: str, display_name: str
) -> models.DbUser:
    user = await query_user(db, provider, provider_id)

    if not user:
        user = models.DbUser(provider=provider, provider_account_id=provider_id, display_name=display_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def query_user(db: database.AsyncSession, provider: str, provider_id: str) -> models.DbUser | None:
    user = (
        await db.exec(
            sqlmodel.select(models.DbUser)
            .filter(models.DbUser.provider == provider)
            .filter(models.DbUser.provider_account_id == provider_id)
        )
    ).one_or_none()

    return user


async def create_tokens(user: models.DbUser) -> protocol.TokenPair:
    access_token = auth.create_access_token(user.id)
    refresh_token = await auth.create_refresh_token(user.id)

    token_pair = protocol.TokenPair(
        access_token=protocol.Token(access_token=access_token, token_type="bearer"),
        refresh_token=protocol.Token(access_token=refresh_token, token_type="refresh"),
    )

    return token_pair


@router.get("/login/debug")
async def login_debug(username: str, state: str = r"{}"):
    # mock code with our own data
    auth_url = f"{settings.api_root}/auth/callback/debug?code={username}&state={state}"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/debug", response_model=protocol.TokenPair)
async def callback_debug(code: str, db: database.AsyncSession = Depends(deps.create_session)):
    """Login using a debug username, which the system will accept unconditionally."""

    username = code
    if not settings.allow_debug_auth:
        raise HTTPException(status_code=403, detail="Debug auth is not allowed")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    # Try to find the user
    user: models.DbUser = (
        await db.exec(sqlmodel.select(models.DbUser).where(models.DbUser.id == username))
    ).one_or_none()

    if user is None:
        logger.info(f"Creating new debug user {username=}")
        user = models.DbUser(id=username, display_name=username, provider="debug", provider_account_id=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new debug user {user=}")

    token_pair = await create_tokens(user)
    return token_pair


@router.post("/trusted")
async def login_trusted(
    db: database.AsyncSession = Depends(deps.create_session),
    trusted_client_token: str = Security(auth.trusted_client_scheme),
):
    if trusted_client_token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    info: TrustedClient = TrustedClientToken(content=trusted_client_token).content
    if info.api_key not in settings.trusted_api_keys_list:
        raise HTTPException(status_code=401, detail="Unauthorized client")

    # Try to find the user
    user: models.DbUser = (
        await db.exec(sqlmodel.select(models.DbUser).where(models.DbUser.id == info.user_id))
    ).one_or_none()

    if user is None:
        logger.info(f"Creating new trusted user {info.username=}")
        user = models.DbUser(
            id=info.user_id,
            display_name=info.username,
            provider=info.client,
            provider_account_id=info.provider_account_id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new trusted user {user=}")
    return user
