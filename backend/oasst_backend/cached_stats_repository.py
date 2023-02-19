from oasst_backend.models import CachedStats, Message, MessageTreeState, User
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas.protocol import AllCachedStatsResponse, CachedStatsName, CachedStatsResponse
from oasst_shared.utils import log_timing, utcnow
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import Session, func, not_


def row_to_dict(r) -> dict:
    return {k: r[k] for k in r.keys()}


class CachedStatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def qry_human_messages_by_lang(self) -> dict[str, int]:
        qry = (
            self.db.query(Message.lang, func.count(Message.id).label("count"))
            .filter(not_(Message.deleted), Message.review_result, not_(Message.synthetic))
            .group_by(Message.lang)
        )
        return {r["lang"]: r["count"] for r in qry}

    def qry_human_messages_by_role(self) -> dict[str, int]:
        qry = (
            self.db.query(Message.role, func.count(Message.id).label("count"))
            .filter(not_(Message.deleted), Message.review_result, not_(Message.synthetic))
            .group_by(Message.role)
        )
        return {r["role"]: r["count"] for r in qry}

    def qry_message_trees_by_state(self) -> dict[str, int]:
        qry = self.db.query(
            MessageTreeState.state, func.count(MessageTreeState.message_tree_id).label("count")
        ).group_by(MessageTreeState.state)
        return {r["state"]: r["count"] for r in qry}

    def qry_message_trees_states_by_lang(self) -> list:
        qry = (
            self.db.query(
                Message.lang, MessageTreeState.state, func.count(MessageTreeState.message_tree_id).label("count")
            )
            .select_from(MessageTreeState)
            .join(Message, MessageTreeState.message_tree_id == Message.id)
            .group_by(MessageTreeState.state, Message.lang)
            .order_by(Message.lang, MessageTreeState.state)
        )
        return [row_to_dict(r) for r in qry]

    def qry_users_accepted_tos(self) -> dict[str, int]:
        qry = self.db.query(func.count(User.id)).filter(User.enabled, User.tos_acceptance_date.is_not(None))
        return {"count": qry.scalar()}

    @log_timing(level="INFO")
    def update_all_cached_stats(self):
        v = self.qry_human_messages_by_lang()
        self._insert_cached_stats(CachedStatsName.human_messages_by_lang, v)

        v = self.qry_human_messages_by_role()
        self._insert_cached_stats(CachedStatsName.human_messages_by_role, v)

        v = self.qry_message_trees_by_state()
        self._insert_cached_stats(CachedStatsName.message_trees_by_state, v)

        v = self.qry_message_trees_states_by_lang()
        self._insert_cached_stats(CachedStatsName.message_trees_states_by_lang, v)

        v = self.qry_users_accepted_tos()
        self._insert_cached_stats(CachedStatsName.users_accepted_tos, v)

    def _insert_cached_stats(self, name: CachedStatsName, stats: dict | list):
        row: CachedStats | None = self.db.query(CachedStats).filter(CachedStats.name == name).one_or_none()
        if row:
            row.modified_date = utcnow()
            row.stats = stats
            flag_modified(row, "stats")
        else:
            row = CachedStats(name=name, modified_date=utcnow(), stats=stats)
        self.db.add(row)

    def get_stats(self, name: CachedStatsName) -> CachedStatsResponse:
        row: CachedStats | None = self.db.query(CachedStats).filter(CachedStats.name == name).one_or_none()
        if not row:
            raise OasstError(f"Cached stats '{name.value}' not found.", OasstErrorCode.CACHED_STATS_NOT_AVAILABLE)
        return CachedStatsResponse(name=row.name, last_updated=row.modified_date, stats=row.stats)

    def get_stats_all(self) -> AllCachedStatsResponse:
        by_name: dict[CachedStatsName, CachedStatsResponse] = {}
        qry = self.db.query(CachedStats)
        for row in qry:
            by_name[row.name] = CachedStatsResponse(name=row.name, last_updated=row.modified_date, stats=row.stats)
        return AllCachedStatsResponse(stats_by_name=by_name)


if __name__ == "__main__":
    # from oasst_backend.api.deps import create_api_client
    from oasst_backend.database import engine

    with Session(engine) as db:
        csr = CachedStatsRepository(db)
        csr.update_all_cached_stats()()
        db.commit()
