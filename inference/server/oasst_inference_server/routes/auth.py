import aiohttp
import fastapi
import sqlmodel
from fastapi import Depends, HTTPException
from loguru import logger
from oasst_inference_server import auth, database, deps, models
from oasst_inference_server.settings import settings
from oasst_shared.schemas import protocol

router = fastapi.APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/login/discord")
async def login_discord():
    redirect_uri = f"{settings.api_root}/auth/callback/discord"
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={settings.auth_discord_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/discord", response_model=protocol.Token)
async def callback_discord(
    code: str,
    db: database.AsyncSession = Depends(deps.create_session),
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
    user: models.DbUser = await query_user_by_provider_id(db, discord_id=discord_id)

    # Create if no user exists
    if not user:
        user = models.DbUser(provider="discord", provider_account_id=discord_id, display_name=discord_username)

        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Discord account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token({"user_id": user.id})

    return protocol.Token(access_token=access_token, token_type="bearer")


async def query_user_by_provider_id(db: database.AsyncSession, discord_id: str | None = None) -> models.DbUser | None:
    """Returns the user associated with a given provider ID if any."""
    user_qry = sqlmodel.select(models.DbUser)

    if discord_id:
        user_qry = user_qry.filter(models.DbUser.provider == "discord").filter(
            models.DbUser.provider_account_id == discord_id
        )
    # elif other IDs...
    else:
        return None

    user: models.DbUser = (await db.exec(user_qry)).first()
    return user


@router.get("/login/debug")
async def login_debug(username: str, db: database.AsyncSession = Depends(deps.create_session)):
    """Login using a debug username, which the system will accept unconditionally."""

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

    # Discord account is authenticated and linked to a user; create JWT
    access_token = auth.create_access_token({"user_id": user.id})

    return protocol.Token(access_token=access_token, token_type="bearer")
