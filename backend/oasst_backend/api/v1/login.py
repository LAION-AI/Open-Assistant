import requests
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


@router.get("/login/discord")
def login_discord(request: Request):
    redirect_uri = get_discord_callback_uri(request)
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={Settings.AUTH_DISCORD_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback/discord", response_model=protocol_schema.Token)
def callback_discord(
    auth_code: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    redirect_uri = get_discord_callback_uri(request)

    # Exchange the auth code for an access token
    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": Settings.AUTH_DISCORD_CLIENT_ID,
            "client_secret": Settings.AUTH_DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "scope": "identify",
        },
    )

    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    # Retrieve user's Discord information using access token
    user_response = requests.get(
        "https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}
    )

    user_response.raise_for_status()
    discord_user = user_response.json()
    discord_user_id = discord_user["id"]

    account: Account = auth.get_account_from_discord_id(db, discord_user_id)

    if not account:
        # Discord account is not linked to an OA account
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)

    # Discord account is valid and linked to an OA account -> create JWT
    access_token = auth.create_access_token(account)

    return protocol_schema.Token(access_token=access_token, token_type="bearer")


def get_discord_callback_uri(request: Request):
    # This seems ugly, not sure if there is a better way
    current_url = str(request.url)
    domain = current_url.split("/api/v1/")[0]
    redirect_uri = f"{domain}/api/v1/callback/discord"
    return redirect_uri
