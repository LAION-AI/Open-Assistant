from typing import Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyCookie
from jose import jwe
from oasst_backend.config import settings
from pydantic import BaseModel, EmailStr

router = APIRouter()

oauth2_scheme = APIKeyCookie(name=settings.AUTH_COOKIE_NAME)


class TokenData(BaseModel):
    """
    A minimal re-creation of the web's token type.  To be expanded later.
    """

    email: Union[EmailStr, None] = None


async def get_current_user(token: str = Security(oauth2_scheme)):
    """
    Decrypts the user's JSON Web Token using HKDF encryption and returns the
    TokenData.
    """
    # We first generate a key from the auth secret.
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=settings.AUTH_LENGTH,
        salt=settings.AUTH_SALT,
        info=settings.AUTH_INFO,
    )
    key = hkdf.derive(settings.AUTH_SECRET)
    # Next we decrypt the JWE token.
    payload = jwe.decrypt(token, key)
    # Finally we have the real token JSON payload and can do whatever we want.
    return TokenData.parse_raw(payload)


@router.get("/check", response_model=str)
async def auth_check(token_data: TokenData = Depends(get_current_user)):
    """Returns the user's email if it can be decrypted."""
    return token_data.email
