import requests
from fastapi import APIRouter, Depends, HTTPException
from oasst_backend import auth
from oasst_backend.api import deps
from oasst_backend.config import Settings
from oasst_backend.models import Account
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()

# TODO: replace placeholder
REDIRECT_URI = "http://localhost:8000/api/v1/callback_discord"


# TODO: make this not only discord
@router.get("/login_discord")
def login_discord():
    # TODO: remove hardcoded URLs
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={Settings.DISCORD_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    raise HTTPException(status_code=302, headers={"location": auth_url})


@router.get("/callback_discord", response_model=protocol_schema.Token)
def callback_discord(
    auth_code: str,
    db: Session = Depends(deps.get_db),
):
    # Exchange the auth code for an access token
    # TODO: remove hardcoded discord URLs
    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": Settings.DISCORD_CLIENT_ID,
            "client_secret": Settings.DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": auth_code,
            # TODO replace this with the URI we want to redirect to, must match the one used when setting up OAuth2 client with Discord
            "redirect_uri": REDIRECT_URI,
            "scope": "identify",
        },
    )

    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    # Retrieve user's Discord information using access token
    # TODO: remove hardcoded discord URLs
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
