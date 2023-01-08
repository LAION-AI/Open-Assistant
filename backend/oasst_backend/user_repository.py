from typing import Optional

from oasst_backend.models import ApiClient, User
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session


class UserRepository:
    def __init__(self, db: Session, api_client: ApiClient):
        self.db = db
        self.api_client = api_client

    def lookup_client_user(self, client_user: protocol_schema.User, create_missing: bool = True) -> Optional[User]:
        if not client_user:
            return None
        user: User = (
            self.db.query(User)
            .filter(
                User.api_client_id == self.api_client.id,
                User.username == client_user.id,
                User.auth_method == client_user.auth_method,
            )
            .first()
        )
        if user is None:
            if create_missing:
                # user is unknown, create new record
                user = User(
                    username=client_user.id,
                    display_name=client_user.display_name,
                    api_client_id=self.api_client.id,
                    auth_method=client_user.auth_method,
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
        elif client_user.display_name and client_user.display_name != user.display_name:
            # we found the user but the display name changed
            user.display_name = client_user.display_name
            self.db.add(user)
            self.db.commit()
        return user
