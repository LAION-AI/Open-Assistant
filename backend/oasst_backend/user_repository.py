from typing import Optional
from uuid import UUID

import oasst_backend.models as models
from oasst_backend.config import settings
from oasst_backend.models import ApiClient, User
from oasst_backend.utils.database_utils import CommitMode, managed_tx_method
from oasst_shared import utils as shared_utils
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.utils import utcnow
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, and_, delete, or_, update
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
    def update_user(
        self,
        id: UUID,
        display_name: Optional[str] = None,
        enabled: Optional[bool] = None,
        notes: Optional[str] = None,
        show_on_leaderboard: Optional[bool] = None,
        tos_acceptance: Optional[bool] = None,
    ) -> User:
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
        if show_on_leaderboard is not None:
            user.show_on_leaderboard = show_on_leaderboard
        if tos_acceptance:
            user.tos_acceptance_date = utcnow()
        if display_name is not None:
            user.display_name = display_name

        self.db.add(user)

        return user

    @managed_tx_method(CommitMode.COMMIT)
    def mark_user_deleted(self, id: UUID) -> None:
        """
        Update a user by global user ID to set deleted flag. Only trusted clients may delete users.
        User deletion anonymises the data of the user.

        Raises:
            OasstError: 403 if untrusted client attempts to delete a user. 404 if user with ID not found.
        """
        if not self.api_client.trusted:
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        user: User = self.db.query(User).filter(User.id == id).first()

        if user is None:
            raise OasstError("User not found", OasstErrorCode.USER_NOT_FOUND, HTTP_404_NOT_FOUND)

        user.deleted = True

        # Anonymise user data
        user.display_name = shared_utils.DELETED_USER_DISPLAY_NAME
        # Ensure uniqueness of (username, auth_method, api_client_id) Index
        user.username = f"{shared_utils.DELETED_USER_ID_PREFIX}{user.id}"
        user.show_on_leaderboard = False

        self.db.add(user)

    @managed_tx_method(CommitMode.COMMIT)
    def _lookup_user_tx(
        self,
        *,
        username: str,
        auth_method: str,
        display_name: Optional[str] = None,
        create_missing: bool = True,
    ) -> User | None:
        user: User = (
            self.db.query(User)
            .filter(
                User.api_client_id == self.api_client.id,
                User.username == username,
                User.auth_method == auth_method,
            )
            .first()
        )
        if user is None:
            if create_missing:
                # user is unknown, create new record
                user = User(
                    username=username,
                    display_name=display_name,
                    api_client_id=self.api_client.id,
                    auth_method=auth_method,
                )
                if auth_method == "system":
                    user.show_on_leaderboard = False  # don't show system users, e.g. import user
                    user.tos_acceptance_date = utcnow()
                self.db.add(user)
        elif display_name and display_name != user.display_name:
            # we found the user but the display name changed
            user.display_name = display_name
            self.db.add(user)

        return user

    def lookup_client_user(self, client_user: protocol_schema.User, create_missing: bool = True) -> User | None:
        if not client_user:
            return None

        if not (client_user.auth_method and client_user.id):
            raise OasstError("Auth method or username missing.", OasstErrorCode.AUTH_AND_USERNAME_REQUIRED)

        num_retries = settings.DATABASE_MAX_TX_RETRY_COUNT
        for i in range(num_retries):
            try:
                return self._lookup_user_tx(
                    username=client_user.id,
                    auth_method=client_user.auth_method,
                    display_name=client_user.display_name,
                    create_missing=create_missing,
                )
            except IntegrityError:
                # catch UniqueViolation exception, for concurrent requests due to conflicts in ix_user_username
                if i + 1 == num_retries:
                    raise

    @managed_tx_method(CommitMode.COMMIT)
    def lookup_system_user(self, username: str, create_missing: bool = True) -> User | None:
        return self._lookup_user_tx(
            username=username,
            auth_method="system",
            display_name=f"__system__/{username}",
            create_missing=create_missing,
        )

    def query_users_ordered_by_username(
        self,
        api_client_id: Optional[UUID] = None,
        gte_username: Optional[str] = None,
        gt_id: Optional[UUID] = None,
        lte_username: Optional[str] = None,
        lt_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
        search_text: Optional[str] = None,
        limit: Optional[int] = 100,
        desc: bool = False,
    ) -> list[User]:
        if not self.api_client.trusted:
            if not api_client_id:
                api_client_id = self.api_client.id

            if api_client_id != self.api_client.id:
                raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        qry = self.db.query(User)

        if gte_username is not None:
            if gt_id:
                qry = qry.filter(
                    or_(User.username > gte_username, and_(User.username == gte_username, User.id > gt_id))
                )
            else:
                qry = qry.filter(User.username >= gte_username)
        elif gt_id:
            raise OasstError("Need id and name for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if lte_username is not None:
            if lt_id:
                qry = qry.filter(
                    or_(User.username < lte_username, and_(User.username == lte_username, User.id < lt_id))
                )
            else:
                qry = qry.filter(User.username <= lte_username)
        elif lt_id:
            raise OasstError("Need id and name for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if auth_method:
            qry = qry.filter(User.auth_method == auth_method)
        if api_client_id:
            qry = qry.filter(User.api_client_id == api_client_id)

        if search_text:
            pattern = "%{}%".format(search_text.replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%"))
            qry = qry.filter(User.username.like(pattern))

        if desc:
            qry = qry.order_by(User.username.desc(), User.id.desc())
        else:
            qry = qry.order_by(User.username, User.id)

        if limit is not None:
            qry = qry.limit(limit)

        return qry.all()

    def query_users_ordered_by_display_name(
        self,
        gte_display_name: Optional[str] = None,
        gt_id: Optional[UUID] = None,
        lte_display_name: Optional[str] = None,
        lt_id: Optional[UUID] = None,
        api_client_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
        search_text: Optional[str] = None,
        limit: Optional[int] = 100,
        desc: bool = False,
    ) -> list[User]:
        if not self.api_client.trusted:
            if not api_client_id:
                # Let unprivileged api clients query their own users without api_client_id being set
                api_client_id = self.api_client.id

            if api_client_id != self.api_client.id:
                # Unprivileged api client asks for foreign users
                raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        qry = self.db.query(User)

        if gte_display_name is not None:
            if gt_id:
                qry = qry.filter(
                    or_(
                        User.display_name > gte_display_name,
                        and_(User.display_name == gte_display_name, User.id > gt_id),
                    )
                )
            else:
                qry = qry.filter(User.display_name >= gte_display_name)
        elif gt_id:
            raise OasstError("Need id and name for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if lte_display_name is not None:
            if lt_id:
                qry = qry.filter(
                    or_(
                        User.display_name < lte_display_name,
                        and_(User.display_name == lte_display_name, User.id < lt_id),
                    )
                )
            else:
                qry = qry.filter(User.display_name <= lte_display_name)
        elif lt_id:
            raise OasstError("Need id and name for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if auth_method:
            qry = qry.filter(User.auth_method == auth_method)
        if api_client_id:
            qry = qry.filter(User.api_client_id == api_client_id)

        if search_text:
            pattern = "%{}%".format(search_text.replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%"))
            qry = qry.filter(User.display_name.like(pattern))

        if auth_method:
            qry = qry.filter(User.auth_method == auth_method)

        if desc:
            qry = qry.order_by(User.display_name.desc(), User.id.desc())
        else:
            qry = qry.order_by(User.display_name, User.id)

        if limit is not None:
            qry = qry.limit(limit)

        return qry.all()

    @managed_tx_method(CommitMode.FLUSH)
    def update_user_last_activity(self, user: User, update_streak: bool = False) -> None:
        current_time = utcnow()
        user.last_activity_date = current_time

        if update_streak:
            if user.streak_last_day_date is None or user.streak_last_day_date > current_time:
                # begin new streak
                user.streak_last_day_date = current_time
                user.streak_days = 0
            else:
                # update streak day count
                user.streak_days = (current_time - user.streak_last_day_date).days

        self.db.add(user)

    @managed_tx_method(CommitMode.FLUSH)
    def merge_users(self, destination_user_id: UUID, source_user_ids: list[UUID]) -> None:
        source_user_ids = list(filter(lambda x: x != destination_user_id, source_user_ids))
        if not source_user_ids:
            return

        # ensure the destination user exists
        self.get_user(id=destination_user_id)

        # update rows in tables that have affected users_ids as FK
        models_to_update = [
            models.Message,
            models.MessageRevision,
            models.MessageReaction,
            models.MessageEmoji,
            models.TextLabels,
            models.Task,
            models.Journal,
        ]
        for table in models_to_update:
            qry = update(table).where(table.user_id.in_(source_user_ids)).values(user_id=destination_user_id)
            self.db.execute(qry)

        # delete rows in user stats tables
        models_to_delete = [models.UserStats, models.TrollStats]
        for table in models_to_delete:
            qry = delete(table).where(table.user_id.in_(source_user_ids))
            self.db.execute(qry)

        # finally delete source users from main user table
        qry = delete(User).where(User.id.in_(source_user_ids))
        self.db.execute(qry)
