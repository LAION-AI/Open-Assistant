from uuid import UUID

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


class TreeManager:
    def __init__(self, db: Session, configuration: TreeManagerConfiguration):
        self.db = db
        self.cfg = configuration

    def next_task(self):
        # 1. determine number of active trees in db
        # active_trees = self.query_num_active_trees()
        pass

    def query_incomplete_rankings(self) -> list:
        """query parents which have childern that need further rankings"""

        statement = text(
            """
SELECT m.parent_id, COUNT(m.id) children_count, MIN(ranking_count) child_min_ranking_count,
    COUNT(m.id) FILTER (WHERE m.ranking_count >= :num_required_rankings) as completed_rankings
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active and mts.state = :ranking_state AND m.review_result AND m.parent_id is NOT NULL
GROUP BY m.parent_id
HAVING COUNT(m.id) > 1 and MIN(ranking_count) < :num_required_rankings;
"""
        )

        r = self.db.execute(
            statement,
            {
                "num_required_rankings": self.cfg.num_required_rankings,
                "ranking_state": message_tree_state.State.RANKING_PHASE,
            },
        )
        return r.all()

    def query_misssing_tree_states(self) -> list[UUID]:
        """find all initial prompt messages that have no associated message tree state"""
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
        """add message tree state rows for all root nodes (inital prompt messages)"""

        with self.db.begin():
            missing_tree_ids = self.query_misssing_tree_states()
            for id in missing_tree_ids:
                logger.info(f"Inserting missing message tree state for message: {id}")
                self._insert_default_state(id)

    def query_num_active_trees(self) -> int:
        query = self.db.query(func.count(MessageTreeState.message_tree_id)).filter(MessageTreeState.active is True)
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
        print("query_num_ranking_tasks", tm.query_incomplete_rankings())
