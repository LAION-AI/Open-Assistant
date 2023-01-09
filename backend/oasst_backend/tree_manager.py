import random
from enum import Enum
from typing import Optional, Tuple
from uuid import UUID

import numpy as np
import pydantic
from loguru import logger
from oasst_backend.api.v1.utils import prepare_conversation
from oasst_backend.models import Message, MessageTreeState, message_tree_state
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
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

    max_children_count: int = 5
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

    mandatory_labels_initial_prompt: Optional[list[protocol_schema.TextLabel]] = [
        protocol_schema.TextLabel.helpful,
        protocol_schema.TextLabel.spam,
    ]
    mandatory_labels_assistant_reply: Optional[list[protocol_schema.TextLabel]] = [
        protocol_schema.TextLabel.helpful,
        protocol_schema.TextLabel.spam,
    ]
    mandatory_labels_prompter_reply: Optional[list[protocol_schema.TextLabel]] = [
        protocol_schema.TextLabel.helpful,
        protocol_schema.TextLabel.spam,
    ]


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
    def __init__(self, db: Session, prompt_repository: PromptRepository, configuration: TreeManagerConfiguration):
        self.db = db
        self.cfg = configuration
        self.pr = prompt_repository

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

    def next_task(self) -> Tuple[protocol_schema.Task, Optional[UUID], Optional[UUID]]:
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

        message_tree_id = None
        parent_message_id = None

        match task_tpye:
            case TaskType.RANKING:
                assert len(incomplete_rankings) > 0
                ranking_parent_id = random.choice(incomplete_rankings).parent_id

                messages = self.pr.fetch_message_conversation(ranking_parent_id)
                conversation = prepare_conversation(messages)
                replies = self.pr.fetch_message_children(ranking_parent_id, reviewed=True, exclude_deleted=True)
                replies = [p.text for p in replies]
                if messages[-1].role == "assistant":
                    logger.info("Generating a RankPrompterRepliesTask.")
                    task = protocol_schema.RankPrompterRepliesTask(conversation=conversation, replies=replies)
                else:
                    logger.info("Generating a RankAssistantRepliesTask.")
                    task = protocol_schema.RankAssistantRepliesTask(conversation=conversation, replies=replies)

            case TaskType.LABEL_REPLY:
                assert len(replies_need_review) > 0
                random_reply_message_id = random.choice(replies_need_review)
                messages = self.pr.fetch_message_conversation(random_reply_message_id)
                conversation = prepare_conversation(messages[:-1])
                message = messages[-1]
                parent_message_id = message.id
                message_tree_id = message.message_tree_id
                if message.role == "assistant":
                    logger.info("Generating a LabelAssistantReplyTask.")
                    task = protocol_schema.LabelAssistantReplyTask(
                        message_id=message.id,
                        conversation=conversation,
                        reply=message.text,
                        valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
                        mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_assistant_reply)),
                    )
                else:
                    logger.info("Generating a LabelPrompterReplyTask.")
                    task = protocol_schema.LabelPrompterReplyTask(
                        message_id=message.id,
                        conversation=conversation,
                        reply=message.text,
                        valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
                        mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_prompter_reply)),
                    )

            case TaskType.REPLY:
                # select a tree with missing replies
                tree_candidates = list(filter(lambda x: x.remaining_messages > 0, active_tree_sizes))
                assert len(tree_candidates) > 0
                source_tree = random.choice(tree_candidates)

                # fetch random conversation in tree
                messages = self.pr.fetch_random_conversation(
                    last_message_role=None, message_tree_id=source_tree.message_tree_id
                )
                conversation = prepare_conversation(messages)

                # generate reply task depending on last message
                if messages[-1].role == "assistant":
                    logger.info("Generating a PrompterReplyTask.")
                    task = protocol_schema.PrompterReplyTask(conversation=conversation)
                else:
                    logger.info("Generating a AssistantReplyTask.")
                    task = protocol_schema.AssistantReplyTask(conversation=conversation)

                message_tree_id = messages[-1].message_tree_id
                parent_message_id = messages[-1].id

            case TaskType.LABEL_PROMPT:
                assert len(prompts_need_review) > 0
                message = self.pr.fetch_message(random.choice(prompts_need_review))
                logger.info("Generating a LabelInitialPromptTask.")
                parent_message_id = message.id
                message_tree_id = message.message_tree_id
                task = protocol_schema.LabelInitialPromptTask(
                    message_id=message.id,
                    prompt=message.text,
                    valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
                    mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_initial_prompt)),
                )

            case TaskType.PROMPT:
                logger.info("Generating an InitialPromptTask.")
                task = protocol_schema.InitialPromptTask(hint=None)

            case _:
                task = None

        logger.info(f"Generated {task=}.")

        return task, message_tree_id, parent_message_id

    def handle_interaction(self, interaction: protocol_schema.AnyInteraction) -> protocol_schema.Task:
        pr = self.pr
        match type(interaction):
            case protocol_schema.TextReplyToMessage:
                logger.info(
                    f"Frontend reports text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                )

                # here we store the text reply in the database
                message = pr.store_text_reply(
                    text=interaction.text,
                    frontend_message_id=interaction.message_id,
                    user_frontend_message_id=interaction.user_message_id,
                )

                if not message.parent_id:
                    logger.info(f"TreeManager: Inserting new tree state for initial prompt {message.id=}")
                    self._insert_default_state(message.id)

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRating:
                logger.info(
                    f"Frontend reports rating of {interaction.message_id=} with {interaction.rating=} by {interaction.user=}."
                )

                # here we store the rating in the database
                pr.store_rating(interaction)

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRanking:
                logger.info(
                    f"Frontend reports ranking of {interaction.message_id=} with {interaction.ranking=} by {interaction.user=}."
                )

                # TODO: check if the ranking is valid
                pr.store_ranking(interaction)
                # here we would store the ranking in the database
                return protocol_schema.TaskDone()
            case protocol_schema.TextLabels:
                logger.info(
                    f"Frontend reports labels of {interaction.message_id=} with {interaction.labels=} by {interaction.user=}."
                )
                pr.store_text_labels(interaction)
                return protocol_schema.TaskDone()
            case _:
                raise OasstError("Invalid response type.", OasstErrorCode.TASK_INVALID_RESPONSE_TYPE)

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
    AND NOT m.deleted
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
    AND NOT m.deleted
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
    AND NOT m.deleted
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
    AND NOT m.deleted
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
    from oasst_backend.api.deps import get_dummy_api_client
    from oasst_backend.database import engine
    from oasst_backend.prompt_repository import PromptRepository

    with Session(engine) as db:
        api_client = get_dummy_api_client(db)
        dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")

        pr = PromptRepository(db=db, api_client=api_client, client_user=dummy_user)

        cfg = TreeManagerConfiguration()
        tm = TreeManager(db, pr, cfg)
        tm.ensure_tree_state()
        print("query_num_active_trees", tm.query_num_active_trees())
        print("query_incomplete_rankings", tm.query_incomplete_rankings())
        print("query_incomplete_reply_reviews", tm.query_replies_need_review())
        print("query_incomplete_initial_prompt_reviews", tm.query_prompts_need_review())
        print("query_active_tree_sizes", tm.query_active_tree_sizes())

        print("next_task:", tm.next_task())
