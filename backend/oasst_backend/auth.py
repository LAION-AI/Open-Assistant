from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from oasst_backend.models import Account
from sqlmodel import Session

SECRET = "test"  # TODO: read this from configuration. maybe use an auth manager object to make this cleaner
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    # TODO store JWT here?
    return encoded_jwt


def get_account_from_discord_user(db: Session, discord_user: dict) -> Optional[Account]:
    account: Account = (
        db.query(Account)
        .filter(
            Account.provider == "discord",
            Account.provider_account_id == discord_user["id"],
        )
        .first()
    )

    return account
