from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.models import (
    Message,
    MessageReaction,
    MessageTreeState,
    Task,
    TextLabels,
    TrollStats,
    User,
    UserStats,
    UserStatsTimeFrame,
)
from oasst_backend.models.db_payload import (
    LabelAssistantReplyPayload,
    LabelInitialPromptPayload,
    LabelPrompterReplyPayload,
    RankingReactionPayload,
)
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_shared.schemas.protocol import (
    EmojiCode,
    LabelTaskMode,
    LeaderboardStats,
    TextLabel,
    TrollboardStats,
    TrollScore,
    UserScore,
)
from oasst_shared.utils import log_timing, utcnow
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.functions import coalesce
from sqlmodel import Session, delete, func, text


def _create_user_score(r, highlighted_user_id: UUID | None) -> UserScore:
    if r["UserStats"]:
        d = r["UserStats"].dict()
    else:
        d = {"modified_date": utcnow()}
    for k in [
        "user_id",
        "username",
        "auth_method",
        "display_name",
        "streak_days",
        "streak_last_day_date",
        "last_activity_date",
    ]:
        d[k] = r[k]
    if highlighted_user_id:
        d["highlighted"] = r["user_id"] == highlighted_user_id
    return UserScore(**d)


def _create_troll_score(r, highlighted_user_id: UUID | None) -> TrollScore:
    if r["TrollStats"]:
        d = r["TrollStats"].dict()
    else:
        d = {"modified_date": utcnow()}
    for k in [
        "user_id",
        "username",
        "auth_method",
        "display_name",
        "last_activity_date",
        "enabled",
        "deleted",
        "show_on_leaderboard",
    ]:
        d[k] = r[k]
    if highlighted_user_id:
        d["highlighted"] = r["user_id"] == highlighted_user_id
    return TrollScore(**d)


class UserStatsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_leaderboard(
        self,
        time_frame: UserStatsTimeFrame,
        limit: int = 100,
        highlighted_user_id: Optional[UUID] = None,
    ) -> LeaderboardStats:
        """
        Get leaderboard stats for the specified time frame
        """

        qry = (
            self.session.query(
                User.id.label("user_id"),
                User.username,
                User.auth_method,
                User.display_name,
                User.streak_days,
                User.streak_last_day_date,
                User.last_activity_date,
                UserStats,
            )
            .join(UserStats, User.id == UserStats.user_id)
            .filter(UserStats.time_frame == time_frame.value, User.show_on_leaderboard, User.enabled)
            .order_by(UserStats.rank)
            .limit(limit)
        )

        leaderboard = [_create_user_score(r, highlighted_user_id) for r in self.session.exec(qry)]
        if len(leaderboard) > 0:
            last_update = max(x.modified_date for x in leaderboard)
        else:
            last_update = utcnow()
        return LeaderboardStats(time_frame=time_frame.value, leaderboard=leaderboard, last_updated=last_update)

    def get_leaderboard_user_window(
        self,
        user: User,
        time_frame: UserStatsTimeFrame,
        window_size: int = 5,
    ) -> LeaderboardStats | None:
        # no window for users who don't show themselves
        if not user.show_on_leaderboard or not user.enabled:
            return None

        qry = self.session.query(UserStats).filter(UserStats.user_id == user.id, UserStats.time_frame == time_frame)
        stats: UserStats = qry.one_or_none()
        if stats is None or stats.rank is None:
            return None

        min_rank = max(0, stats.rank - window_size // 2)
        max_rank = min_rank + window_size

        qry = (
            self.session.query(
                User.id.label("user_id"),
                User.username,
                User.auth_method,
                User.display_name,
                User.streak_days,
                User.streak_last_day_date,
                User.last_activity_date,
                UserStats,
            )
            .join(UserStats, User.id == UserStats.user_id)
            .filter(UserStats.time_frame == time_frame.value, User.show_on_leaderboard, User.enabled)
            .where(UserStats.rank >= min_rank, UserStats.rank <= max_rank)
            .order_by(UserStats.rank)
        )

        leaderboard = [_create_user_score(r, highlighted_user_id=user.id) for r in self.session.exec(qry)]
        if len(leaderboard) > 0:
            last_update = max(x.modified_date for x in leaderboard)
        else:
            last_update = utcnow()
        return LeaderboardStats(time_frame=time_frame.value, leaderboard=leaderboard, last_updated=last_update)

    def get_user_stats_all_time_frames(self, user_id: UUID) -> dict[str, UserScore | None]:
        qry = (
            self.session.query(
                User.id.label("user_id"),
                User.username,
                User.auth_method,
                User.display_name,
                User.streak_days,
                User.streak_last_day_date,
                User.last_activity_date,
                UserStats,
            )
            .outerjoin(UserStats, User.id == UserStats.user_id)
            .filter(User.id == user_id)
        )

        stats_by_timeframe = {}
        for r in self.session.exec(qry):
            us = r["UserStats"]
            if us is not None:
                stats_by_timeframe[us.time_frame] = _create_user_score(r, user_id)
            else:
                stats_by_timeframe = {tf.value: _create_user_score(r, user_id) for tf in UserStatsTimeFrame}
        return stats_by_timeframe

    def get_trollboard(
        self,
        time_frame: UserStatsTimeFrame,
        limit: int = 100,
        enabled: Optional[bool] = None,
        highlighted_user_id: Optional[UUID] = None,
    ) -> TrollboardStats:
        """
        Get trollboard stats for the specified time frame
        """

        qry = (
            self.session.query(
                User.id.label("user_id"),
                User.username,
                User.auth_method,
                User.display_name,
                User.last_activity_date,
                User.enabled,
                User.deleted,
                User.show_on_leaderboard,
                TrollStats,
            )
            .join(TrollStats, User.id == TrollStats.user_id)
            .filter(TrollStats.time_frame == time_frame.value)
        )

        if enabled is not None:
            qry = qry.filter(User.enabled == enabled)

        qry = qry.order_by(TrollStats.rank).limit(limit)

        trollboard = [_create_troll_score(r, highlighted_user_id) for r in self.session.exec(qry)]
        if len(trollboard) > 0:
            last_update = max(x.modified_date for x in trollboard)
        else:
            last_update = utcnow()
        return TrollboardStats(time_frame=time_frame.value, trollboard=trollboard, last_updated=last_update)

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
            if mode == LabelTaskMode.simple:
                s.labels_simple = count
            elif mode == LabelTaskMode.full:
                s.labels_full = count

        qry = self.query_labels_by_mode_per_user(
            payload_type=LabelPrompterReplyPayload.__name__, reference_time=base_date
        )
        for r in qry:
            uid, mode, count = r
            s = get_stats(uid)
            if mode == LabelTaskMode.simple:
                s.labels_simple += count
            elif mode == LabelTaskMode.full:
                s.labels_full += count

        qry = self.query_labels_by_mode_per_user(
            payload_type=LabelInitialPromptPayload.__name__, reference_time=base_date
        )
        for r in qry:
            uid, mode, count = r
            s = get_stats(uid)
            if mode == LabelTaskMode.simple:
                s.labels_simple += count
            elif mode == LabelTaskMode.full:
                s.labels_full += count

        qry = self.query_rankings_per_user(reference_time=base_date)
        for r in qry:
            uid, count = r
            get_stats(uid).rankings_total = count

        rank_field_names = ["reply_ranked_1", "reply_ranked_2", "reply_ranked_3"]
        for i, fn in enumerate(rank_field_names):
            qry = self.query_ranking_result_users(reference_time=base_date, rank=i)
            for r in qry:
                uid, count = r
                setattr(get_stats(uid), fn, count)

        # delete all existing stast for time frame
        d = delete(UserStats).where(UserStats.time_frame == time_frame_key)
        self.session.execute(d)

        if None in stats_by_user:
            logger.warning("Some messages in DB have NULL values in user_id column.")
            del stats_by_user[None]

        # compute magic leader score
        for v in stats_by_user.values():
            v.leader_score = v.compute_leader_score()

        # insert user objects
        self.session.add_all(stats_by_user.values())
        self.session.flush()

        self.update_leader_ranks(time_frame=time_frame)

    def query_message_emoji_counts_per_user(self, reference_time: Optional[datetime] = None):
        qry = self.session.query(
            Message.user_id,
            func.sum(coalesce(Message.emojis[EmojiCode.thumbs_up].cast(sa.Integer), 0)).label("up"),
            func.sum(coalesce(Message.emojis[EmojiCode.thumbs_down].cast(sa.Integer), 0)).label("down"),
            func.sum(coalesce(Message.emojis[EmojiCode.red_flag].cast(sa.Integer), 0)).label("flag"),
        ).filter(Message.deleted == sa.false(), Message.emojis.is_not(None))

        if reference_time:
            qry = qry.filter(Message.created_date >= reference_time)

        qry = qry.group_by(Message.user_id)
        return qry

    def query_spam_prompts_per_user(self, reference_time: Optional[datetime] = None):
        qry = (
            self.session.query(Message.user_id, func.count().label("spam_prompts"))
            .select_from(MessageTreeState)
            .join(Message, MessageTreeState.message_tree_id == Message.id)
            .filter(MessageTreeState.state == TreeState.ABORTED_LOW_GRADE)
        )

        if reference_time:
            qry = qry.filter(Message.created_date >= reference_time)

        qry = qry.group_by(Message.user_id)
        return qry

    def query_labels_per_user(self, reference_time: Optional[datetime] = None):
        qry = (
            self.session.query(
                Message.user_id,
                func.sum(coalesce(TextLabels.labels[TextLabel.spam].cast(sa.Integer), 0)).label("spam"),
                func.sum(coalesce(TextLabels.labels[TextLabel.lang_mismatch].cast(sa.Integer), 0)).label(
                    "lang_mismach"
                ),
                func.sum(coalesce(TextLabels.labels[TextLabel.not_appropriate].cast(sa.Integer), 0)).label(
                    "not_appropriate"
                ),
                func.sum(coalesce(TextLabels.labels[TextLabel.pii].cast(sa.Integer), 0)).label("pii"),
                func.sum(coalesce(TextLabels.labels[TextLabel.hate_speech].cast(sa.Integer), 0)).label("hate_speech"),
                func.sum(coalesce(TextLabels.labels[TextLabel.sexual_content].cast(sa.Integer), 0)).label(
                    "sexual_content"
                ),
                func.sum(coalesce(TextLabels.labels[TextLabel.political_content].cast(sa.Integer), 0)).label(
                    "political_content"
                ),
                func.avg(TextLabels.labels[TextLabel.quality].cast(sa.Float)).label("quality"),
                func.avg(TextLabels.labels[TextLabel.humor].cast(sa.Float)).label("humor"),
                func.avg(TextLabels.labels[TextLabel.toxicity].cast(sa.Float)).label("toxicity"),
                func.avg(TextLabels.labels[TextLabel.violence].cast(sa.Float)).label("violence"),
                func.avg(TextLabels.labels[TextLabel.helpfulness].cast(sa.Float)).label("helpfulness"),
            )
            .select_from(TextLabels)
            .join(Message, TextLabels.message_id == Message.id)
            .filter(Message.deleted == sa.false(), Message.emojis.is_not(None))
        )

        if reference_time:
            qry = qry.filter(Message.created_date >= reference_time)

        qry = qry.group_by(Message.user_id)
        return qry

    def _update_troll_stats_internal(self, time_frame: UserStatsTimeFrame, base_date: Optional[datetime] = None):
        # gather user data

        time_frame_key = time_frame.value

        stats_by_user: dict[UUID, TrollStats] = dict()
        now = utcnow()

        def get_stats(id: UUID) -> TrollStats:
            us = stats_by_user.get(id)
            if not us:
                us = TrollStats(user_id=id, time_frame=time_frame_key, modified_date=now, base_date=base_date)
                stats_by_user[id] = us
            return us

        # emoji counts of user's messages
        qry = self.query_message_emoji_counts_per_user(reference_time=base_date)
        for r in qry:
            uid = r["user_id"]
            s = get_stats(uid)
            s.upvotes = r["up"]
            s.downvotes = r["down"]
            s.red_flags = r["flag"]

        # num spam prompts
        qry = self.query_spam_prompts_per_user(reference_time=base_date)
        for r in qry:
            uid, count = r
            s = get_stats(uid).spam_prompts = count

        label_field_names = (
            "quality",
            "humor",
            "toxicity",
            "violence",
            "helpfulness",
            "spam",
            "lang_mismach",
            "not_appropriate",
            "pii",
            "hate_speech",
            "sexual_content",
            "political_content",
        )

        # label counts / mean values
        qry = self.query_labels_per_user(reference_time=base_date)
        for r in qry:
            uid = r["user_id"]
            s = get_stats(uid)
            for fn in label_field_names:
                setattr(s, fn, r[fn])

        # delete all existing stast for time frame
        d = delete(TrollStats).where(TrollStats.time_frame == time_frame_key)
        self.session.execute(d)

        if None in stats_by_user:
            logger.warning("Some messages in DB have NULL values in user_id column.")
            del stats_by_user[None]

        # compute magic leader score
        for v in stats_by_user.values():
            v.troll_score = v.compute_troll_score()

        # insert user objects
        self.session.add_all(stats_by_user.values())
        self.session.flush()

        self.update_troll_ranks(time_frame=time_frame)

    @log_timing(log_kwargs=True)
    def update_leader_ranks(self, time_frame: UserStatsTimeFrame = None):
        """
        Update user_stats ranks. The persisted rank values allow to
        quickly the rank of a single user and to query nearby users.
        """

        # todo: convert sql to sqlalchemy query..
        # ranks = self.session.query(
        #     func.row_number()
        #     .over(partition_by=UserStats.time_frame, order_by=[UserStats.leader_score.desc(), UserStats.user_id])
        #     .label("rank"),
        #     UserStats.user_id,
        #     UserStats.time_frame,
        # )

        sql_update_rank = """
-- update rank
UPDATE user_stats us
SET "rank" = r."rank"
FROM
    (SELECT
        ROW_NUMBER () OVER(
            PARTITION BY time_frame
            ORDER BY leader_score DESC, user_id
        ) AS "rank", user_id, time_frame
    FROM user_stats us2
    INNER JOIN "user" u ON us2.user_id = u.id AND u.show_on_leaderboard AND u.enabled
    WHERE (:time_frame IS NULL OR time_frame = :time_frame)) AS r
WHERE
    us.user_id = r.user_id
    AND us.time_frame = r.time_frame;"""
        r = self.session.execute(
            text(sql_update_rank), {"time_frame": time_frame.value if time_frame is not None else None}
        )
        logger.debug(f"pre_compute_ranks leader updated({time_frame=}) {r.rowcount} rows.")

    @log_timing(log_kwargs=True)
    def update_troll_ranks(self, time_frame: UserStatsTimeFrame = None):
        sql_update_troll_rank = """
-- update rank
UPDATE troll_stats ts
SET "rank" = r."rank"
FROM
    (SELECT
        ROW_NUMBER () OVER(
            PARTITION BY time_frame
            ORDER BY troll_score DESC, user_id
        ) AS "rank", user_id, time_frame
    FROM troll_stats ts2
    WHERE (:time_frame IS NULL OR time_frame = :time_frame)) AS r
WHERE
    ts.user_id = r.user_id
    AND ts.time_frame = r.time_frame;"""
        r = self.session.execute(
            text(sql_update_troll_rank), {"time_frame": time_frame.value if time_frame is not None else None}
        )
        logger.debug(f"pre_compute_ranks troll updated({time_frame=}) {r.rowcount} rows.")

    def update_stats_time_frame(
        self,
        time_frame: UserStatsTimeFrame,
        reference_time: Optional[datetime] = None,
        leader_stats: bool = True,
        troll_stats: bool = True,
    ):
        if leader_stats:
            self._update_stats_internal(time_frame, reference_time)
        if troll_stats:
            self._update_troll_stats_internal(time_frame, reference_time)
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
