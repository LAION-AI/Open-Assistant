from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.models import Message, MessageReaction, Task, User, UserStats, UserStatsTimeFrame
from oasst_backend.models.db_payload import (
    LabelAssistantReplyPayload,
    LabelPrompterReplyPayload,
    RankingReactionPayload,
)
from oasst_shared.schemas.protocol import LeaderboardStats, UserScore
from oasst_shared.utils import log_timing, utcnow
from sqlalchemy.dialects import postgresql
from sqlmodel import Session, delete, func, select, update


def _create_user_score(r):
    if r["UserStats"]:
        d = r["UserStats"].dict()
    else:
        d = {"modified_date": utcnow()}
    for k in ["user_id", "username", "auth_method", "display_name"]:
        d[k] = r[k]
    return UserScore(**d)


class UserStatsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_leaderboard(self, time_frame: UserStatsTimeFrame, limit: int = 100) -> LeaderboardStats:
        """
        Get leaderboard stats for the specified time frame
        """

        qry = (
            self.session.query(User.id.label("user_id"), User.username, User.auth_method, User.display_name, UserStats)
            .join(UserStats, User.id == UserStats.user_id)
            .filter(UserStats.time_frame == time_frame.value)
            .order_by(UserStats.rank)
            .limit(limit)
        )

        leaderboard = [_create_user_score(r) for r in self.session.exec(qry)]
        if len(leaderboard) > 0:
            last_update = max(x.modified_date for x in leaderboard)
        else:
            last_update = utcnow()
        return LeaderboardStats(time_frame=time_frame.value, leaderboard=leaderboard, last_updated=last_update)

    def get_user_stats_all_time_frames(self, user_id: UUID) -> dict[str, UserScore | None]:
        qry = (
            self.session.query(User.id.label("user_id"), User.username, User.auth_method, User.display_name, UserStats)
            .outerjoin(UserStats, User.id == UserStats.user_id)
            .filter(User.id == user_id)
        )

        stats_by_timeframe = {}
        for r in self.session.exec(qry):
            us = r["UserStats"]
            if us is not None:
                stats_by_timeframe[us.time_frame] = _create_user_score(r)
            else:
                stats_by_timeframe = {tf.value: _create_user_score(r) for tf in UserStatsTimeFrame}
        return stats_by_timeframe

    def query_total_prompts_per_user(
        self, reference_time: Optional[datetime] = None, only_reviewed: Optional[bool] = True
    ):
        qry = self.session.query(Message.user_id, func.count()).filter(
            Message.deleted == sa.false(), Message.parent_id.is_(None)
        )
        if reference_time:
            qry = qry.filter(Message.created_date >= reference_time)
        if only_reviewed:
            qry = qry.filter(Message.review_result == sa.true())
        qry = qry.group_by(Message.user_id)
        return qry

    def query_replies_by_role_per_user(
        self, reference_time: Optional[datetime] = None, only_reviewed: Optional[bool] = True
    ) -> list:
        qry = self.session.query(Message.user_id, Message.role, func.count()).filter(
            Message.deleted == sa.false(), Message.parent_id.is_not(None)
        )
        if reference_time:
            qry = qry.filter(Message.created_date >= reference_time)
        if only_reviewed:
            qry = qry.filter(Message.review_result == sa.true())
        qry = qry.group_by(Message.user_id, Message.role)
        return qry

    def query_labels_by_mode_per_user(
        self, payload_type: str = LabelAssistantReplyPayload.__name__, reference_time: Optional[datetime] = None
    ):
        qry = self.session.query(Task.user_id, Task.payload["payload", "mode"].astext, func.count()).filter(
            Task.done == sa.true(), Task.payload_type == payload_type
        )
        if reference_time:
            qry = qry.filter(Task.created_date >= reference_time)
        qry = qry.group_by(Task.user_id, Task.payload["payload", "mode"].astext)
        return qry

    def query_rankings_per_user(self, reference_time: Optional[datetime] = None):
        qry = self.session.query(MessageReaction.user_id, func.count()).filter(
            MessageReaction.payload_type == RankingReactionPayload.__name__
        )
        if reference_time:
            qry = qry.filter(MessageReaction.created_date >= reference_time)
        qry = qry.group_by(MessageReaction.user_id)
        return qry

    def query_ranking_result_users(self, rank: int = 0, reference_time: Optional[datetime] = None):
        ranked_message_id = MessageReaction.payload["payload", "ranked_message_ids", rank].astext.cast(
            postgresql.UUID(as_uuid=True)
        )
        qry = (
            self.session.query(Message.user_id, func.count())
            .select_from(MessageReaction)
            .join(Message, ranked_message_id == Message.id)
            .filter(MessageReaction.payload_type == RankingReactionPayload.__name__)
        )
        if reference_time:
            qry = qry.filter(MessageReaction.created_date >= reference_time)
        qry = qry.group_by(Message.user_id)
        return qry

    def _update_stats_internal(self, time_frame: UserStatsTimeFrame, base_date: Optional[datetime] = None):
        # gather user data

        time_frame_key = time_frame.value

        stats_by_user: dict[UUID, UserStats] = dict()
        now = utcnow()

        def get_stats(id: UUID) -> UserStats:
            us = stats_by_user.get(id)
            if not us:
                us = UserStats(user_id=id, time_frame=time_frame_key, modified_date=now, base_date=base_date)
                stats_by_user[id] = us
            return us

        # total prompts
        qry = self.query_total_prompts_per_user(reference_time=base_date, only_reviewed=False)
        for r in qry:
            uid, count = r
            get_stats(uid).prompts = count

        # accepted prompts
        qry = self.query_total_prompts_per_user(reference_time=base_date, only_reviewed=True)
        for r in qry:
            uid, count = r
            get_stats(uid).accepted_prompts = count

        # total replies
        qry = self.query_replies_by_role_per_user(reference_time=base_date, only_reviewed=False)
        for r in qry:
            uid, role, count = r
            s = get_stats(uid)
            if role == "assistant":
                s.replies_assistant += count
            elif role == "prompter":
                s.replies_prompter += count

        # accepted replies
        qry = self.query_replies_by_role_per_user(reference_time=base_date, only_reviewed=True)
        for r in qry:
            uid, role, count = r
            s = get_stats(uid)
            if role == "assistant":
                s.accepted_replies_assistant += count
            elif role == "prompter":
                s.accepted_replies_prompter += count

        # simple and full labels
        qry = self.query_labels_by_mode_per_user(
            payload_type=LabelAssistantReplyPayload.__name__, reference_time=base_date
        )
        for r in qry:
            uid, mode, count = r
            s = get_stats(uid)
            if mode == "simple":
                s.labels_simple = count
            elif mode == "full":
                s.labels_full = count

        qry = self.query_labels_by_mode_per_user(
            payload_type=LabelPrompterReplyPayload.__name__, reference_time=base_date
        )
        for r in qry:
            uid, mode, count = r
            s = get_stats(uid)
            if mode == "simple":
                s.labels_simple += count
            elif mode == "full":
                s.labels_full += count

        qry = self.query_rankings_per_user(reference_time=base_date)
        for r in qry:
            uid, count = r
            get_stats(uid).rankings_total = count

        rank_field_names = ["reply_ranked_1", "reply_ranked_2", "reply_ranked_3"]
        for i, fn in enumerate(rank_field_names):
            qry = self.query_ranking_result_users(reference_time=base_date, rank=0)
            for r in qry:
                uid, count = r
                setattr(get_stats(uid), fn, count)

        # delete all existing stast for time frame
        d = delete(UserStats).where(UserStats.time_frame == time_frame_key)
        self.session.execute(d)

        # compute magic leader score
        for v in stats_by_user.values():
            v.leader_score = v.compute_leader_score()

        # insert user objects
        self.session.add_all(stats_by_user.values())
        self.session.flush()

        self.update_ranks(time_frame=time_frame)

    @log_timing(log_kwargs=True)
    def update_ranks(self, time_frame: UserStatsTimeFrame = None):
        """
        Update user_stats ranks. The persisted rank values allow to
        quickly the rank of a single user and to query nearby users.
        """
        try:
            # sql alchemy implementation
            subquery = (
                select(
                    [
                        func.row_number()
                        .over(
                            partition_by=UserStats.time_frame,
                            order_by=[UserStats.leader_score.desc(), UserStats.user_id],
                        )
                        .label("rank"),
                        UserStats.user_id,
                        UserStats.time_frame,
                    ]
                )
                .where(UserStats.time_frame == time_frame.value if time_frame is not None else None)
                .alias()
            )

            update_stmt = (
                update(UserStats)
                .where(UserStats.user_id == subquery.c.user_id)
                .where(UserStats.time_frame == subquery.c.time_frame)
                .values(rank=subquery.c.rank)
            )
            qry = self.session.execute(update_stmt)
            logger.debug(f"pre_compute_ranks updated({time_frame=}) {qry.rowcount} rows.")
        except Exception:
            logger.error(f"pre_compute_ranks failed({time_frame=})")

    def update_stats_time_frame(self, time_frame: UserStatsTimeFrame, reference_time: Optional[datetime] = None):
        self._update_stats_internal(time_frame, reference_time)
        self.session.commit()

    @log_timing(log_kwargs=True, level="INFO")
    def update_stats(self, *, time_frame: UserStatsTimeFrame):
        now = utcnow()
        match time_frame:
            case UserStatsTimeFrame.day:
                r = now - timedelta(days=1)
                self.update_stats_time_frame(time_frame, r)

            case UserStatsTimeFrame.week:
                r = now.date() - timedelta(days=7)
                r = datetime(r.year, r.month, r.day, tzinfo=now.tzinfo)
                self.update_stats_time_frame(time_frame, r)

            case UserStatsTimeFrame.month:
                r = now.date() - timedelta(days=30)
                r = datetime(r.year, r.month, r.day, tzinfo=now.tzinfo)
                self.update_stats_time_frame(time_frame, r)

            case UserStatsTimeFrame.total:
                self.update_stats_time_frame(time_frame, None)

    @log_timing(level="INFO")
    def update_multiple_time_frames(self, time_frames: list[UserStatsTimeFrame]):
        for t in time_frames:
            self.update_stats(time_frame=t)

    @log_timing(level="INFO")
    def update_all_time_frames(self):
        self.update_multiple_time_frames(list(UserStatsTimeFrame))


if __name__ == "__main__":
    from oasst_backend.api.deps import api_auth
    from oasst_backend.database import engine

    with Session(engine) as db:
        api_client = api_auth(settings.OFFICIAL_WEB_API_KEY, db=db)
        usr = UserStatsRepository(db)
        usr.update_all_time_frames()
        db.commit()
