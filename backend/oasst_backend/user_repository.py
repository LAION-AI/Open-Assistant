from typing import Optional
from uuid import UUID

from oasst_backend.models import ApiClient, Message, User
from oasst_backend.utils.database_utils import CommitMode, managed_tx_method
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.schemas.protocol import LeaderboardStats
from sqlmodel import Session, func
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


class UserRepository:
    def __init__(self, db: Session, api_client: ApiClient):
        self.db = db
        self.api_client = api_client

    def get_user(self, id: UUID, api_client_id: Optional[UUID] = None) -> User:
        """
        Get a user by global user ID. All clients may get users with the same API client ID as the querying client.
        Trusted clients can get any user.

        Raises:
            OasstError: 403 if untrusted client attempts to query foreign users. 404 if user with ID not found.
        """
        if not self.api_client.trusted and api_client_id is None:
            api_client_id = self.api_client.id

        if not self.api_client.trusted and api_client_id != self.api_client.id:
            # Unprivileged client requests foreign user
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        # Will always be unique
        user_query = self.db.query(User).filter(User.id == id)

        if api_client_id:
            user_query = user_query.filter(User.api_client_id == api_client_id)

        user: User = user_query.first()

        if user is None:
            raise OasstError("User not found", OasstErrorCode.USER_NOT_FOUND, HTTP_404_NOT_FOUND)

        return user

    def query_frontend_user(
        self, auth_method: str, username: str, api_client_id: Optional[UUID] = None
    ) -> Optional[User]:
        if not api_client_id:
            api_client_id = self.api_client.id

        if not self.api_client.trusted and api_client_id != self.api_client.id:
            # Unprivileged API client asks for foreign user
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        user: User = (
            self.db.query(User)
            .filter(User.auth_method == auth_method, User.username == username, User.api_client_id == api_client_id)
            .first()
        )

        if user is None:
            raise OasstError("User not found", OasstErrorCode.USER_NOT_FOUND, HTTP_404_NOT_FOUND)

        return user

    @managed_tx_method(CommitMode.COMMIT)
    def update_user(self, id: UUID, enabled: Optional[bool] = None, notes: Optional[str] = None) -> None:
        """
        Update a user by global user ID to disable or set admin notes. Only trusted clients may update users.

        Raises:
            OasstError: 403 if untrusted client attempts to update a user. 404 if user with ID not found.
        """
        if not self.api_client.trusted:
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        user: User = self.db.query(User).filter(User.id == id).first()

        if user is None:
            raise OasstError("User not found", OasstErrorCode.USER_NOT_FOUND, HTTP_404_NOT_FOUND)

        if enabled is not None:
            user.enabled = enabled
        if notes is not None:
            user.notes = notes

        self.db.add(user)

    @managed_tx_method(CommitMode.COMMIT)
    def mark_user_deleted(self, id: UUID) -> None:
        """
        Update a user by global user ID to set deleted flag. Only trusted clients may delete users.

        Raises:
            OasstError: 403 if untrusted client attempts to delete a user. 404 if user with ID not found.
        """
        if not self.api_client.trusted:
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        user: User = self.db.query(User).filter(User.id == id).first()

        if user is None:
            raise OasstError("User not found", OasstErrorCode.USER_NOT_FOUND, HTTP_404_NOT_FOUND)

        user.deleted = True

        self.db.add(user)

    @managed_tx_method(CommitMode.COMMIT)
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
        elif client_user.display_name and client_user.display_name != user.display_name:
            # we found the user but the display name changed
            user.display_name = client_user.display_name
            self.db.add(user)
        return user

    def get_user_leaderboard(self, role: str) -> LeaderboardStats:
        """
        Get leaderboard stats for Messages created,
        separate leaderboard for prompts & assistants

        """
        query = (
            self.db.query(Message.user_id, User.username, User.display_name, func.count(Message.user_id))
            .join(User, User.id == Message.user_id, isouter=True)
            .filter(Message.deleted is not True, Message.role == role)
            .group_by(Message.user_id, User.username, User.display_name)
            .order_by(func.count(Message.user_id).desc())
        )

        result = [
            {"ranking": i, "user_id": j[0], "username": j[1], "display_name": j[2], "score": j[3]}
            for i, j in enumerate(query.all(), start=1)
        ]

        return LeaderboardStats(leaderboard=result)

    def query_users(
        self,
        api_client_id: Optional[UUID] = None,
        limit: Optional[int] = 20,
        gte: Optional[str] = None,
        lt: Optional[str] = None,
        auth_method: Optional[str] = None,
    ) -> list[User]:
        if not self.api_client.trusted:
            if not api_client_id:
                api_client_id = self.api_client.id

            if api_client_id != self.api_client.id:
                raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        users = self.db.query(User)

        if api_client_id:
            users = users.filter(User.api_client_id == api_client_id)

        if auth_method:
            users = users.filter(User.auth_method == auth_method)

        users = users.order_by(User.display_name)

        if gte:
            users = users.filter(User.display_name >= gte)

        if lt:
            users = users.filter(User.display_name < lt)

        if limit is not None:
            users = users.limit(limit)

        return users.all()

    def query_users_by_display_name(
        self,
        search_text: str,
        exact: Optional[bool] = False,
        limit: Optional[int] = 20,
        api_client_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
    ) -> list[User]:
        if not self.api_client.trusted:
            if not api_client_id:
                api_client_id = self.api_client.id

            if api_client_id != self.api_client.id:
                raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        qry = self.db.query(User).order_by(User.display_name)

        if exact:
            qry = qry.filter(User.display_name == search_text)
        else:
            pattern = "%{}%".format(search_text.replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%"))
            qry = qry.filter(User.display_name.like(pattern))

        if auth_method:
            qry = qry.filter(User.auth_method == auth_method)

        if limit is not None:
            qry = qry.limit(limit)

        return qry.all()
