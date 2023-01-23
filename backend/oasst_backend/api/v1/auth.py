from typing import Union

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = APIKeyCookie(name="next-auth.session-token")

SECRET_KEY = "O/M2uIbGj+lDD2oyNa8ax4jEOJqCPJzO53UbWShmq98="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenData(BaseModel):
    sub: Union[str, None] = None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("get_current_user")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(payload)
    sub: str = payload.get("sub")
    if sub is None:
        raise credentials_exception
    return TokenData(sub=sub)


@router.get("/check", response_model=str)
async def auth_check(token_data: TokenData = Depends(get_current_user)):
    return token_data.sub
