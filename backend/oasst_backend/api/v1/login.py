import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from oasst_backend import auth
from oasst_backend.api import deps
from oasst_backend.config import Settings
from oasst_backend.models import Account
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()


@router.get("/discord")
def login_discord(request: Request):
    redirect_uri = f"{get_callback_uri(request)}/discord"
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={Settings.AUTH_DISCORD_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/discord", response_model=protocol_schema.Token)
async def callback_discord(
    auth_code: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    redirect_uri = f"{get_callback_uri(request)}/discord"

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        # Exchange the auth code for a Discord access token
        async with session.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": Settings.AUTH_DISCORD_CLIENT_ID,
                "client_secret": Settings.AUTH_DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "scope": "identify",
            },
        ) as token_response:
            token_response_json = await token_response.json()
            access_token = token_response_json["access_token"]

        # Retrieve user's Discord information using access token
        async with session.get(
            "https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}
        ) as user_response:
            user_response_json = await user_response.json()
            discord_id = user_response_json["id"]

    account: Account = auth.get_account_from_discord_id(db, discord_id)

    if not account:
        # Discord account is not linked to an OA account
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)

    # Discord account is valid and linked to an OA account -> create JWT
    access_token = auth.create_access_token(account)

    return protocol_schema.Token(access_token=access_token, token_type="bearer")


def get_callback_uri(request: Request):
    """
    Gets the URI for the base callback endpoint with no provider name appended.
    """
    # This seems ugly, not sure if there is a better way
    current_url = str(request.url)
    domain = current_url.split("/api/v1/")[0]
    redirect_uri = f"{domain}/api/v1/callback"
    return redirect_uri
