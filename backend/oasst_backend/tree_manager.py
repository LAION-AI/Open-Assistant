from enum import Enum
from uuid import UUID

import numpy as np
import pydantic
from loguru import logger
from oasst_backend.models import Message, MessageTreeState, message_tree_state
from sqlalchemy.sql import text
from sqlmodel import Session, func


class TreeManagerConfiguration(pydantic.BaseModel):
    """Configuration class for the TreeManager"""

    max_active_trees: int = 100
    """Maximum number of concurrently active trees in the database.
    No new initial prompt tasks will be handed out to users if this
    number is reached."""

    max_tree_depth: int = 6
    """Maximum depth of message tree."""

    max_children_count: int = 6
    """Maximum number of reply messages per tree node."""

    goal_tree_size: int = 30
    """Total number of messages to gather per tree"""

    num_reviews_initial_prompt: int = 5
    """Number of peer review checks to collect in INITIAL_PROMPT_REVIEW phase."""

    num_reviews_reply: int = 3
    """Number of peer review checks to collect per reply (other than initial_prompt)"""

    acceptance_threshold_initial_prompt: float = 0.6
    """Threshold for accepting an initial prompt"""

    acceptance_threshold_reply: float = 0.6
    """Threshold for accepting a reply"""

    num_required_rankings: int = 5
    """Number of rankings in which the message participated."""


class TaskType(Enum):
    NONE = -1
    RANKING = 0
    LABEL_REPLY = 1
    REPLY = 2
    LABEL_PROMPT = 3
    PROMPT = 4


class ActiveTreeSizeRow(pydantic.BaseModel):
    message_tree_id: UUID
    tree_size: int
    goal_tree_size: int

    @property
    def remaining_messages(self) -> int:
        return max(0, self.goal_tree_size - self.tree_size)

    class Config:
        orm_mode = True


class IncompleteRankingsRow(pydantic.BaseModel):
    parent_id: UUID
    children_count: int
    child_min_ranking_count: int

    class Config:
        orm_mode = True


class TreeManager:
    def __init__(self, db: Session, configuration: TreeManagerConfiguration):
        self.db = db
        self.cfg = configuration

    def _task_selection(
        self,
        num_ranking_tasks: int,
        num_replies_need_review: int,
        num_prompts_need_review: int,
        num_missing_prompts: int,
        num_missing_replies: int,
    ) -> TaskType:
        """
        Determines which task to hand out to human worker.
        The task type is drawn with relative weight (e.g. ranking has highest priority)
        depending on what is possible with the current message trees in the database.
        """

        logger.debug(
            f"TreeManager._task_selection({num_ranking_tasks=}, {num_replies_need_review=}, "
            f"{num_prompts_need_review=}, {num_missing_prompts=}, {num_missing_replies=})"
        )

        task_weights = [0] * 5

        if num_ranking_tasks > 0:
            task_weights[TaskType.RANKING.value] = 10

        if num_replies_need_review > 0:
            task_weights[TaskType.LABEL_REPLY.value] = 2

        if num_prompts_need_review > 0:
            task_weights[TaskType.LABEL_PROMPT.value] = 1

        if num_missing_replies > 0:
            task_weights[TaskType.REPLY.value] = 2

        if num_missing_prompts > 0:
            task_weights[TaskType.PROMPT.value] = 1

        task_weights = np.array(task_weights)
        weight_sum = task_weights.sum()
        if weight_sum < 1e-8:
            task_type = TaskType.NONE
        else:
            task_weights = task_weights / weight_sum
            task_type = TaskType(np.random.choice(a=len(task_weights), p=task_weights))

        logger.debug(f"Selected task type: {task_type}")
        return TaskType(task_type)

    def next_task(self):
        # 1. determine type of task to generate

        num_active_trees = self.query_num_active_trees()
        prompts_need_review = self.query_prompts_need_review()
        replies_need_review = self.query_replies_need_review()
        incomplete_rankings = self.query_incomplete_rankings()
        active_tree_sizes = self.query_active_tree_sizes()

        num_missing_replies = sum(x.remaining_messages for x in active_tree_sizes)

        task_tpye = self._task_selection(
            num_ranking_tasks=len(incomplete_rankings),
            num_replies_need_review=len(replies_need_review),
            num_prompts_need_review=len(prompts_need_review),
            num_missing_prompts=max(0, self.cfg.max_active_trees - num_active_trees),
            num_missing_replies=num_missing_replies,
        )

        # todo task construction
        logger.info(task_tpye)

    def query_prompts_need_review(self) -> list[UUID]:
        """
        Select id of initial prompts with less then required rankings in active message tree
        (active == True in message_tree_state)
        """

        qry = text(
            """
SELECT m.id
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.id
WHERE mts.state = :state
    AND NOT m.review_result
    AND m.review_count < :num_required_reviews
    AND m.parent_id is NULL;"""
        )
        r = self.db.execute(
            qry,
            {
                "state": message_tree_state.State.INITIAL_PROMPT_REVIEW,
                "num_required_reviews": self.cfg.num_reviews_initial_prompt,
            },
        )
        return [x["id"] for x in r.all()]

    def query_replies_need_review(self) -> list[UUID]:
        """
        Select ids of child messages (parent_id IS NOT NULL) with less then required rankings
        in active message tree (active == True in message_tree_state)
        """

        qry = text(
            """
SELECT m.id
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.state = :breedin_state
    AND NOT m.review_result
    AND m.review_count < :num_required_reviews
    AND m.parent_id is NOT NULL;"""
        )
        r = self.db.execute(
            qry,
            {
                "breedin_state": message_tree_state.State.BREEDING_PHASE,
                "num_required_reviews": self.cfg.num_reviews_reply,
            },
        )
        return [x["id"] for x in r.all()]

    def query_incomplete_rankings(self) -> list[IncompleteRankingsRow]:
        """Query parents which have childern that need further rankings"""

        qry = text(
            """
SELECT m.parent_id, COUNT(m.id) children_count, MIN(m.ranking_count) child_min_ranking_count,
    COUNT(m.id) FILTER (WHERE m.ranking_count >= :num_required_rankings) as completed_rankings
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active
    AND mts.state = :ranking_state
    AND m.review_result
    AND m.parent_id IS NOT NULL
GROUP BY m.parent_id
HAVING COUNT(m.id) > 1 and MIN(m.ranking_count) < :num_required_rankings;"""
        )

        r = self.db.execute(
            qry,
            {
                "num_required_rankings": self.cfg.num_required_rankings,
                "ranking_state": message_tree_state.State.RANKING_PHASE,
            },
        )
        return [IncompleteRankingsRow.from_orm(x) for x in r.all()]

    def query_active_tree_sizes(self) -> list[ActiveTreeSizeRow]:
        """Query size of active message trees in breeding phase."""

        qry = text(
            """
SELECT m.message_tree_id, mts.goal_tree_size, COUNT(m.id) AS tree_size
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active
    AND mts.state = :breedin_state
    AND (m.review_count < :num_required_reviews OR m.review_result OR m.parent_id IS NULL)
GROUP BY m.message_tree_id, mts.goal_tree_size;"""
        )

        r = self.db.execute(
            qry,
            {
                "breedin_state": message_tree_state.State.BREEDING_PHASE,
                "num_required_reviews": self.cfg.num_reviews_reply,
            },
        )
        return [ActiveTreeSizeRow.from_orm(x) for x in r.all()]

    def query_misssing_tree_states(self) -> list[UUID]:
        """Find all initial prompt messages that have no associated message tree state"""
        qry_missing_tree_states = (
            self.db.query(Message.id)
            .join(MessageTreeState, isouter=True)
            .filter(
                Message.parent_id.is_(None),
                Message.message_tree_id == Message.id,
                MessageTreeState.message_tree_id.is_(None),
            )
        )

        return [m.id for m in qry_missing_tree_states.all()]

    def ensure_tree_state(self):
        """Add message tree state rows for all root nodes (inital prompt messages)."""

        with self.db.begin():
            missing_tree_ids = self.query_misssing_tree_states()
            for id in missing_tree_ids:
                logger.info(f"Inserting missing message tree state for message: {id}")
                self._insert_default_state(id)

    def query_num_active_trees(self) -> int:
        query = self.db.query(func.count(MessageTreeState.message_tree_id)).filter(MessageTreeState.active)
        return query.scalar()

    def _insert_tree_state(
        self,
        root_message_id: UUID,
        goal_tree_size: int,
        max_depth: int,
        max_children_count: int,
        active: bool,
        state: message_tree_state.State = message_tree_state.State.INITIAL_PROMPT_REVIEW,
    ) -> MessageTreeState:
        model = MessageTreeState(
            message_tree_id=root_message_id,
            goal_tree_size=goal_tree_size,
            max_depth=max_depth,
            max_children_count=max_children_count,
            state=state.value,
            active=active,
            accepted_messages=0,
        )

        self.db.add(model)
        return model

    def _insert_default_state(self, root_message_id: UUID) -> MessageTreeState:
        return self._insert_tree_state(
            root_message_id=root_message_id,
            goal_tree_size=self.cfg.goal_tree_size,
            max_depth=self.cfg.max_tree_depth,
            max_children_count=self.cfg.max_children_count,
            state=message_tree_state.State.INITIAL_PROMPT_REVIEW,
            active=True,
        )


if __name__ == "__main__":
    from oasst_backend.database import engine

    with Session(engine) as db:
        cfg = TreeManagerConfiguration()
        tm = TreeManager(db, cfg)
        tm.ensure_tree_state()
        print("query_num_active_trees", tm.query_num_active_trees())
        print("query_incomplete_rankings", tm.query_incomplete_rankings())
        print("query_incomplete_reply_reviews", tm.query_replies_need_review())
        print("query_incomplete_initial_prompt_reviews", tm.query_prompts_need_review())
        print("query_active_tree_sizes", tm.query_active_tree_sizes())

        print("next_task:", tm.next_task())
