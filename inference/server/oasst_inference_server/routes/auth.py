import aiohttp
import fastapi
import sqlmodel
from fastapi import Depends, HTTPException, Security
from loguru import logger
from oasst_inference_server import auth, database, deps, models
from oasst_inference_server.settings import settings
from oasst_shared.schemas import protocol

router = fastapi.APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/check")
async def check_user_auth(user_id: str = Depends(auth.get_current_user_id)):
    return user_id


@router.get("/providers")
async def get_available_auth_providers():
    # this could be computed once on startup since it is not likely to change
    providers = [
        key
        for key, is_available in {
            "debug": settings.allow_debug_auth,
            "discord": settings.auth_discord_client_id,
            "github": settings.auth_github_client_id,
        }.items()
        if is_available
    ]
    if len(providers) == 0:
        logger.warn("No login providers available, logging in is not possible.")
    return providers


@router.get("/refresh", response_model=protocol.Token)
async def refresh_token(refresh_token: str = Security(auth.refresh_scheme)):
    access_token = await auth.refresh_access_token(refresh_token)
    return protocol.Token(access_token=access_token, token_type="bearer")


@router.get("/login/discord")
async def login_discord(state: str = r"{}"):
    redirect_uri = f"{settings.auth_callback_root}/discord"
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={settings.auth_discord_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify&state={state}"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/discord", response_model=protocol.TokenPair)
async def callback_discord(
    code: str,
    db: database.AsyncSession = Depends(deps.create_session),
):
    redirect_uri = f"{settings.auth_callback_root}/discord"

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
    user: models.DbUser = await query_user_by_provider_id(db, discord_id=discord_id)

    # Create if no user exists
    if not user:
        user = models.DbUser(provider="discord", provider_account_id=discord_id, display_name=discord_username)

        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Discord account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token(user.id)
    refresh_token = await auth.create_refresh_token(user.id)

    token_pair = protocol.TokenPair(
        access_token=protocol.Token(access_token=access_token, token_type="bearer"),
        refresh_token=protocol.Token(access_token=refresh_token, token_type="refresh"),
    )

    return token_pair


@router.get("/login/github")
async def login_github(state: str = r"{}"):
    redirect_uri = f"{settings.auth_callback_root}/github"
    auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.auth_github_client_id}&redirect_uri={redirect_uri}&state={state}"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/github", response_model=protocol.TokenPair)
async def callback_github(
    code: str,
    db: database.AsyncSession = Depends(deps.create_session),
):
    redirect_uri = f"{settings.auth_callback_root}/github"

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        # Exchange the auth code for a GitHub access token
        async with session.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.auth_github_client_id,
                "client_secret": settings.auth_github_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        ) as token_response:
            token_response_json = await token_response.json()

        try:
            access_token = token_response_json["access_token"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid access token response from GitHub")

        # Retrieve user's GitHub information using access token
        async with session.get(
            "https://api.github.com/user", headers={"Authorization": f"Bearer {access_token}"}
        ) as user_response:
            user_response_json = await user_response.json()

    try:
        github_id = str(user_response_json["id"])
        github_username = user_response_json["login"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid user info response from GitHub")

    # Try to find a user in our DB linked to the GitHub user
    user: models.DbUser = await query_user_by_provider_id(db, github_id=github_id)

    # Create if no user exists
    if not user:
        user = models.DbUser(provider="github", provider_account_id=github_id, display_name=github_username)

        db.add(user)
        await db.commit()
        await db.refresh(user)

    # GitHub account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token(user.id)
    refresh_token = await auth.create_refresh_token(user.id)

    token_pair = protocol.TokenPair(
        access_token=protocol.Token(access_token=access_token, token_type="bearer"),
        refresh_token=protocol.Token(access_token=refresh_token, token_type="refresh"),
    )

    return token_pair


async def query_user_by_provider_id(
    db: database.AsyncSession,
    discord_id: str | None = None,
    github_id: str | None = None,
) -> models.DbUser | None:
    """Returns the user associated with a given provider ID if any."""
    user_qry = sqlmodel.select(models.DbUser)

    if discord_id:
        user_qry = user_qry.filter(models.DbUser.provider == "discord").filter(
            models.DbUser.provider_account_id == discord_id
        )
    elif github_id:
        user_qry = user_qry.filter(models.DbUser.provider == "github").filter(
            models.DbUser.provider_account_id == github_id
        )
    else:
        return None

    user: models.DbUser = (await db.exec(user_qry)).first()
    return user


@router.get("/login/debug")
async def login_debug(username: str, state: str = r"{}"):
    # mock code with our own data
    auth_url = f"{settings.auth_callback_root}/debug?code={username}&state={state}"
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

    # User exists; create JWT
    access_token = auth.create_access_token(user.id)
    refresh_token = await auth.create_refresh_token(user.id)

    token_pair = protocol.TokenPair(
        access_token=protocol.Token(access_token=access_token, token_type="bearer"),
        refresh_token=protocol.Token(access_token=refresh_token, token_type="refresh"),
    )

    return token_pair
