from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from oasst_backend.config import Settings
from oasst_backend.models import Account
from sqlmodel import Session


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=Settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings.AUTH_SECRET, algorithm=Settings.AUTH_ALGORITHM)
    # TODO store JWT here?
    return encoded_jwt


def get_account_from_discord_id(db: Session, discord_id: str) -> Optional[Account]:
    account: Account = (
        db.query(Account)
        .filter(
            Account.provider == "discord",
            Account.provider_account_id == discord_id,
        )
        .first()
    )

    return account
