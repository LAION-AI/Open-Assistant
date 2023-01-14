import random
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
import pydantic
from loguru import logger
from oasst_backend.api.v1.utils import prepare_conversation, prepare_conversation_message_list
from oasst_backend.config import settings
from oasst_backend.models import Message, MessageReaction, MessageTreeState, TextLabels, message_tree_state
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.utils.hugging_face import HfClassificationModel, HfEmbeddingModel, HfUrl, HuggingFaceAPI
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlalchemy.sql import text
from sqlmodel import Session, func


class TreeManagerConfiguration(pydantic.BaseModel):
    """TreeManager configuration settings"""

    max_active_trees: int = 10
    """Maximum number of concurrently active message trees in the database.
    No new initial prompt tasks are handed out to users if this
    number is reached."""

    max_tree_depth: int = 6
    """Maximum depth of message tree."""

    max_children_count: int = 5
    """Maximum number of reply messages per tree node."""

    goal_tree_size: int = 15
    """Total number of messages to gather per tree"""

    num_reviews_initial_prompt: int = 3
    """Number of peer review checks to collect in INITIAL_PROMPT_REVIEW state."""

    num_reviews_reply: int = 3
    """Number of peer review checks to collect per reply (other than initial_prompt)"""

    p_full_labeling_review_prompt: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for initial prompts"""

    p_full_labeling_review_reply_assistant: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for assistant replies"""

    p_full_labeling_review_reply_prompter: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for prompter replies"""

    acceptance_threshold_initial_prompt: float = 0.6
    """Threshold for accepting an initial prompt"""

    acceptance_threshold_reply: float = 0.6
    """Threshold for accepting a reply"""

    num_required_rankings: int = 3
    """Number of rankings in which the message participated."""

    mandatory_labels_initial_prompt: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]
    mandatory_labels_assistant_reply: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]
    mandatory_labels_prompter_reply: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]


class TaskType(Enum):
    NONE = -1
    RANKING = 0
    LABEL_REPLY = 1
    REPLY = 2
    LABEL_PROMPT = 3
    PROMPT = 4


class TaskRole(Enum):
    ANY = 0
    PROMPTER = 1
    ASSISTANT = 2


class ActiveTreeSizeRow(pydantic.BaseModel):
    message_tree_id: UUID
    tree_size: int
    goal_tree_size: int

    @property
    def remaining_messages(self) -> int:
        return max(0, self.goal_tree_size - self.tree_size)

    class Config:
        orm_mode = True


class ExtendibleParentRow(pydantic.BaseModel):
    parent_id: UUID
    depth: int
    message_tree_id: UUID
    active_children_count: int

    class Config:
        orm_mode = True


class IncompleteRankingsRow(pydantic.BaseModel):
    parent_id: UUID
    children_count: int
    child_min_ranking_count: int

    class Config:
        orm_mode = True


class TreeManager:
    _all_text_labels = list(map(lambda x: x.value, protocol_schema.TextLabel))

    def __init__(self, db: Session, prompt_repository: PromptRepository, configuration: TreeManagerConfiguration):
        self.db = db
        self.cfg = configuration
        self.pr = prompt_repository

    def _task_selection(
        self,
        desired_task_type: protocol_schema.TaskRequestType,
        num_ranking_tasks: int,
        num_replies_need_review: int,
        num_prompts_need_review: int,
        num_missing_prompts: int,
        num_missing_replies: int,
    ) -> Tuple[TaskType, TaskRole]:
        """
        Determines which task to hand out to human worker.
        The task type is drawn with relative weight (e.g. ranking has highest priority)
        depending on what is possible with the current message trees in the database.
        """

        logger.debug(
            f"TreeManager._task_selection({num_ranking_tasks=}, {num_replies_need_review=}, "
            f"{num_prompts_need_review=}, {num_missing_prompts=}, {num_missing_replies=})"
        )

        task_type = TaskType.NONE
        task_role = TaskRole.ANY
        if desired_task_type == protocol_schema.TaskRequestType.random:
            task_weights = [0] * 5

            if num_ranking_tasks > 0:
                task_weights[TaskType.RANKING.value] = 10

            if num_replies_need_review > 0:
                task_weights[TaskType.LABEL_REPLY.value] = 5

            if num_prompts_need_review > 0:
                task_weights[TaskType.LABEL_PROMPT.value] = 5

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
        else:
            match desired_task_type:
                case protocol_schema.TaskRequestType.initial_prompt:
                    if num_missing_prompts > 0:
                        task_type = TaskType.PROMPT
                case protocol_schema.TaskRequestType.label_initial_prompt:
                    if num_prompts_need_review > 0:
                        task_type = TaskType.LABEL_PROMPT
                case protocol_schema.TaskRequestType.assistant_reply | protocol_schema.TaskRequestType.prompter_reply:
                    if num_missing_replies > 0:
                        task_role = (
                            TaskRole.ASSISTANT
                            if desired_task_type == protocol_schema.TaskRequestType.assistant_reply
                            else TaskRole.PROMPTER
                        )
                        task_type = TaskType.REPLY
                case protocol_schema.TaskRequestType.label_assistant_reply | protocol_schema.TaskRequestType.label_prompter_reply:
                    if num_replies_need_review > 0:
                        task_role = (
                            TaskRole.ASSISTANT
                            if desired_task_type == protocol_schema.TaskRequestType.label_assistant_reply
                            else TaskRole.PROMPTER
                        )
                        task_type = TaskType.LABEL_REPLY
                case protocol_schema.TaskRequestType.rank_assistant_replies | protocol_schema.TaskRequestType.rank_prompter_replies:
                    if num_ranking_tasks > 0:
                        task_role = (
                            TaskRole.ASSISTANT
                            if desired_task_type == protocol_schema.TaskRequestType.rank_assistant_replies
                            else TaskRole.PROMPTER
                        )
                        task_type = TaskType.RANKING

        logger.debug(f"Selected {task_type=}, {task_role=}")
        return task_type, task_role

    def next_task(
        self, desired_task_type: protocol_schema.TaskRequestType
    ) -> Tuple[protocol_schema.Task, Optional[UUID], Optional[UUID]]:

        logger.debug("TreeManager.next_task()")

        num_active_trees = self.query_num_active_trees()
        prompts_need_review = self.query_prompts_need_review()
        replies_need_review = self.query_replies_need_review()
        incomplete_rankings = self.query_incomplete_rankings()
        active_tree_sizes = self.query_extendible_trees()

        # determine type of task to generate
        num_missing_replies = sum(x.remaining_messages for x in active_tree_sizes)

        task_type, task_role = self._task_selection(
            desired_task_type,
            num_ranking_tasks=len(incomplete_rankings),
            num_replies_need_review=len(replies_need_review),
            num_prompts_need_review=len(prompts_need_review),
            num_missing_prompts=max(0, self.cfg.max_active_trees - num_active_trees),
            num_missing_replies=num_missing_replies,
        )

        if task_type == TaskType.NONE:
            raise OasstError(
                f"No tasks of type '{desired_task_type.value}' are currently available.",
                OasstErrorCode.TASK_REQUESTED_TYPE_NOT_AVAILABLE,
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        if task_role != TaskRole.ANY:
            # Todo: Allow role specific message selection...
            raise OasstError(
                f"No tasks of type '{desired_task_type.value}' are currently available.",
                OasstErrorCode.TASK_REQUESTED_TYPE_NOT_AVAILABLE,
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        message_tree_id = None
        parent_message_id = None

        logger.debug(f"selected {task_type=}")
        match task_type:
            case TaskType.RANKING:
                assert len(incomplete_rankings) > 0
                ranking_parent_id = random.choice(incomplete_rankings).parent_id

                messages = self.pr.fetch_message_conversation(ranking_parent_id)
                conversation = prepare_conversation(messages)
                replies = self.pr.fetch_message_children(ranking_parent_id, reviewed=True, exclude_deleted=True)

                assert len(replies) > 1
                random.shuffle(replies)  # hand out replies in random order
                reply_messages = prepare_conversation_message_list(replies)
                replies = [p.text for p in replies]

                if messages[-1].role == "assistant":
                    logger.info("Generating a RankPrompterRepliesTask.")
                    task = protocol_schema.RankPrompterRepliesTask(
                        conversation=conversation, replies=replies, reply_messages=reply_messages
                    )
                else:
                    logger.info("Generating a RankAssistantRepliesTask.")
                    task = protocol_schema.RankAssistantRepliesTask(
                        conversation=conversation, replies=replies, reply_messages=reply_messages
                    )

                parent_message_id = ranking_parent_id
                message_tree_id = messages[-1].message_tree_id

            case TaskType.LABEL_REPLY:
                assert len(replies_need_review) > 0
                random_reply_message_id = random.choice(replies_need_review)
                messages = self.pr.fetch_message_conversation(random_reply_message_id)

                conversation = prepare_conversation(messages[:-1])
                message = messages[-1]

                self.cfg.p_full_labeling_review_reply_prompter: float = 0.1

                label_mode = protocol_schema.LabelTaskMode.full
                valid_labels = self._all_text_labels

                if message.role == "assistant":
                    if random.random() > self.cfg.p_full_labeling_review_reply_assistant:
                        valid_labels = list(map(lambda x: x.value, self.cfg.mandatory_labels_assistant_reply))
                        label_mode = protocol_schema.LabelTaskMode.simple
                    logger.info(f"Generating a LabelAssistantReplyTask. ({label_mode=:s})")
                    task = protocol_schema.LabelAssistantReplyTask(
                        message_id=message.id,
                        conversation=conversation,
                        reply=message.text,
                        valid_labels=valid_labels,
                        mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_assistant_reply)),
                        mode=label_mode,
                    )
                else:
                    if random.random() > self.cfg.p_full_labeling_review_reply_prompter:
                        valid_labels = list(map(lambda x: x.value, self.cfg.mandatory_labels_prompter_reply))
                        label_mode = protocol_schema.LabelTaskMode.simple
                    logger.info(f"Generating a LabelPrompterReplyTask. ({label_mode=:s})")
                    task = protocol_schema.LabelPrompterReplyTask(
                        message_id=message.id,
                        conversation=conversation,
                        reply=message.text,
                        valid_labels=valid_labels,
                        mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_prompter_reply)),
                        mode=label_mode,
                    )

                parent_message_id = message.id
                message_tree_id = message.message_tree_id

            case TaskType.REPLY:
                # select a tree with missing replies
                extensible_parents = self.query_extendible_parents()
                assert len(extensible_parents) > 0

                # fetch random conversation to extend
                random_parent = random.choice(extensible_parents)
                logger.debug(f"selected {random_parent=}")
                messages = self.pr.fetch_message_conversation(random_parent.parent_id)
                assert all(m.review_result for m in messages)  # ensure all messages have positive review
                conversation = prepare_conversation(messages)

                # generate reply task depending on last message
                if messages[-1].role == "assistant":
                    logger.info("Generating a PrompterReplyTask.")
                    task = protocol_schema.PrompterReplyTask(conversation=conversation)
                else:
                    logger.info("Generating a AssistantReplyTask.")
                    task = protocol_schema.AssistantReplyTask(conversation=conversation)

                parent_message_id = messages[-1].id
                message_tree_id = messages[-1].message_tree_id

            case TaskType.LABEL_PROMPT:
                assert len(prompts_need_review) > 0
                message = self.pr.fetch_message(random.choice(prompts_need_review))

                label_mode = protocol_schema.LabelTaskMode.full
                valid_labels = self._all_text_labels

                if random.random() > self.cfg.p_full_labeling_review_prompt:
                    valid_labels = list(map(lambda x: x.value, self.cfg.mandatory_labels_initial_prompt))
                    label_mode = protocol_schema.LabelTaskMode.simple

                logger.info(f"Generating a LabelInitialPromptTask ({label_mode=:s}).")
                task = protocol_schema.LabelInitialPromptTask(
                    message_id=message.id,
                    prompt=message.text,
                    valid_labels=valid_labels,
                    mandatory_labels=list(map(lambda x: x.value, self.cfg.mandatory_labels_initial_prompt)),
                    mode=label_mode,
                )

                parent_message_id = message.id
                message_tree_id = message.message_tree_id

            case TaskType.PROMPT:
                logger.info("Generating an InitialPromptTask.")
                task = protocol_schema.InitialPromptTask(hint=None)

            case _:
                task = None

        logger.info(f"Generated {task=}.")

        return task, message_tree_id, parent_message_id

    async def handle_interaction(self, interaction: protocol_schema.AnyInteraction) -> protocol_schema.Task:
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
                    self.db.commit()

                if not settings.DEBUG_SKIP_EMBEDDING_COMPUTATION:
                    try:
                        hugging_face_api = HuggingFaceAPI(
                            f"{HfUrl.HUGGINGFACE_FEATURE_EXTRACTION.value}/{HfEmbeddingModel.MINILM.value}"
                        )
                        embedding = await hugging_face_api.post(interaction.text)
                        pr.insert_message_embedding(
                            message_id=message.id, model=HfEmbeddingModel.MINILM.value, embedding=embedding
                        )
                    except OasstError:
                        logger.error(
                            f"Could not fetch embbeddings for text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                        )

                if not settings.DEBUG_SKIP_TOXICITY_CALCULATION:
                    try:
                        model_name: str = HfClassificationModel.TOXIC_ROBERTA.value
                        hugging_face_api: HuggingFaceAPI = HuggingFaceAPI(
                            f"{HfUrl.HUGGINGFACE_FEATURE_EXTRACTION.value}/{model_name}"
                        )

                        toxicity: List[List[Dict[str, Any]]] = await hugging_face_api.post(interaction.text)
                        toxicity = toxicity[0][0]

                        pr.insert_toxicity(
                            message_id=message.id, model=model_name, score=toxicity["score"], label=toxicity["label"]
                        )

                    except OasstError:
                        logger.error(
                            f"Could not compute toxicity for  text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                        )

            case protocol_schema.MessageRating:
                logger.info(
                    f"Frontend reports rating of {interaction.message_id=} with {interaction.rating=} by {interaction.user=}."
                )

                pr.store_rating(interaction)

            case protocol_schema.MessageRanking:
                logger.info(
                    f"Frontend reports ranking of {interaction.message_id=} with {interaction.ranking=} by {interaction.user=}."
                )

                _, task = pr.store_ranking(interaction)

                self.check_condition_for_scoring_state(task.message_tree_id)

            case protocol_schema.TextLabels:
                logger.info(
                    f"Frontend reports labels of {interaction.message_id=} with {interaction.labels=} by {interaction.user=}."
                )

                _, task, msg = pr.store_text_labels(interaction)

                # if it was a respones for a task, check if we have enough reviews to calc review_result
                if task and msg:
                    reviews = self.query_reviews_for_message(msg.id)
                    acceptance_score = self._calculate_acceptance(reviews)
                    logger.debug(
                        f"Message {msg.id=}, {acceptance_score=}, {len(reviews)=}, {msg.review_result=}, {msg.review_count=}"
                    )
                    if msg.parent_id is None:
                        if not msg.review_result and msg.review_count >= self.cfg.num_reviews_initial_prompt:
                            if acceptance_score > self.cfg.acceptance_threshold_initial_prompt:
                                msg.review_result = True
                                self.db.add(msg)
                                self.db.commit()
                                logger.info(
                                    f"Initial prompt message was accepted: {msg.id=}, {acceptance_score=}, {len(reviews)=}"
                                )
                            else:
                                self.enter_low_grade_state(msg.message_tree_id)
                        self.check_condition_for_growing_state(msg.message_tree_id)
                    elif msg.review_count >= self.cfg.num_reviews_reply:
                        if not msg.review_result and acceptance_score > self.cfg.acceptance_threshold_reply:
                            msg.review_result = True
                            self.db.add(msg)
                            self.db.commit()
                            logger.info(
                                f"Reply message message accepted: {msg.id=}, {acceptance_score=}, {len(reviews)=}"
                            )

                    self.check_condition_for_ranking_state(msg.message_tree_id)

            case _:
                raise OasstError("Invalid response type.", OasstErrorCode.TASK_INVALID_RESPONSE_TYPE)

        return protocol_schema.TaskDone()

    def _enter_state(self, mts: MessageTreeState, state: message_tree_state.State):
        assert mts and mts.active

        is_terminal = state in message_tree_state.TERMINAL_STATES

        if is_terminal:
            mts.active = False
        mts.state = state.value
        self.db.add(mts)
        self.db.commit()

        if is_terminal:
            logger.info(f"Tree entered terminal '{mts.state}' state ({mts.message_tree_id=})")
        else:
            logger.info(f"Tree entered '{mts.state}' state ({mts.message_tree_id=})")

    def enter_low_grade_state(self, message_tree_id: UUID) -> None:
        logger.debug(f"enter_low_grade_state({message_tree_id=})")
        mts = self.pr.fetch_tree_state(message_tree_id)
        self._enter_state(mts, message_tree_state.State.ABORTED_LOW_GRADE)

    def check_condition_for_growing_state(self, message_tree_id: UUID) -> bool:
        logger.debug(f"check_condition_for_growing_state({message_tree_id=})")

        mts = self.pr.fetch_tree_state(message_tree_id)
        if not mts.active or mts.state != message_tree_state.State.INITIAL_PROMPT_REVIEW:
            logger.debug(f"False {mts.active=}, {mts.state=}")
            return False

        # check if initial prompt was accepted
        initial_prompt = self.pr.fetch_message(message_tree_id)
        if not initial_prompt.review_result:
            logger.debug(f"False {initial_prompt.review_result=}")
            return False

        self._enter_state(mts, message_tree_state.State.GROWING)
        return True

    def check_condition_for_ranking_state(self, message_tree_id: UUID) -> bool:
        logger.debug(f"check_condition_for_ranking_state({message_tree_id=})")

        mts = self.pr.fetch_tree_state(message_tree_id)
        if not mts.active or mts.state != message_tree_state.State.GROWING:
            logger.debug(f"False {mts.active=}, {mts.state=}")
            return False

        # check if desired tree size has been reached and all nodes have been reviewed
        tree_size = self.query_tree_size(message_tree_id)
        if tree_size.remaining_messages > 0:
            logger.debug(f"False {tree_size.remaining_messages=}")
            return False

        self._enter_state(mts, message_tree_state.State.RANKING)
        return True

    def check_condition_for_scoring_state(self, message_tree_id: UUID) -> bool:
        logger.debug(f"check_condition_for_scoring_state({message_tree_id=})")
        mts: MessageTreeState
        mts = self.db.query(MessageTreeState).filter(MessageTreeState.message_tree_id == message_tree_id).one()
        if not mts.active or mts.state != message_tree_state.State.RANKING:
            logger.debug(f"False {mts.active=}, {mts.state=}")
            return False

        rankings_by_message = self.query_tree_ranking_results(message_tree_id)
        for parent_msg_id, ranking in rankings_by_message.items():
            if len(ranking) < self.cfg.num_required_rankings:
                logger.debug(f"False {parent_msg_id=} {len(ranking)=}")
                return False

        self._enter_state(mts, message_tree_state.State.READY_FOR_SCORING)
        return True

    def _calculate_acceptance(self, labels: list[TextLabels]):
        # calculate acceptance based on spam label
        return np.mean([1 - l.labels[protocol_schema.TextLabel.spam] for l in labels])

    _sql_find_prompts_need_review = """
-- find initial prompts that need more reviews
SELECT m.id
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.id
WHERE mts.active
    AND mts.state = :state
    AND NOT m.review_result
    AND NOT m.deleted
    AND m.review_count < :num_reviews_initial_prompt
    AND m.parent_id is NULL
    AND (:excluded_user_id IS NULL OR m.user_id != :excluded_user_id)
"""

    def query_prompts_need_review(self) -> list[UUID]:
        """
        Select id of initial prompts with less then required rankings in active message tree
        (active == True in message_tree_state)
        """

        r = self.db.execute(
            text(self._sql_find_prompts_need_review),
            {
                "state": message_tree_state.State.INITIAL_PROMPT_REVIEW,
                "num_reviews_initial_prompt": self.cfg.num_reviews_initial_prompt,
                "excluded_user_id": None if settings.DEBUG_ALLOW_SELF_LABELING else self.pr.user_id,
            },
        )
        return [x["id"] for x in r.all()]

    _sql_find_replies_need_review = """
SELECT m.id
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active
    AND mts.state = :breeding_state
    AND NOT m.review_result
    AND NOT m.deleted
    AND m.review_count < :num_required_reviews
    AND m.parent_id is NOT NULL
    AND (:excluded_user_id IS NULL OR m.user_id != :excluded_user_id)
"""

    def query_replies_need_review(self) -> list[UUID]:
        """
        Select ids of child messages (parent_id IS NOT NULL) with less then required rankings
        in active message tree (active == True in message_tree_state)
        """

        r = self.db.execute(
            text(self._sql_find_replies_need_review),
            {
                "breeding_state": message_tree_state.State.GROWING,
                "num_required_reviews": self.cfg.num_reviews_reply,
                "excluded_user_id": None if settings.DEBUG_ALLOW_SELF_LABELING else self.pr.user_id,
            },
        )
        return [x["id"] for x in r.all()]

    _sql_find_incomplete_rankings = """
-- find incomplete rankings
SELECT m.parent_id, COUNT(m.id) children_count, MIN(m.ranking_count) child_min_ranking_count,
    COUNT(m.id) FILTER (WHERE m.ranking_count >= :num_required_rankings) as completed_rankings
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active                        -- only consider active trees
    AND mts.state = :ranking_state      -- message tree must be in ranking state
    AND m.review_result                 -- must be reviewed
    AND NOT m.deleted                   -- not deleted
    AND m.parent_id IS NOT NULL         -- ignore initial prompts
GROUP BY m.parent_id
HAVING COUNT(m.id) > 1 and MIN(m.ranking_count) < :num_required_rankings
"""

    def query_incomplete_rankings(self) -> list[IncompleteRankingsRow]:
        """Query parents which have childern that need further rankings"""

        r = self.db.execute(
            text(self._sql_find_incomplete_rankings),
            {
                "num_required_rankings": self.cfg.num_required_rankings,
                "ranking_state": message_tree_state.State.RANKING,
            },
        )
        return [IncompleteRankingsRow.from_orm(x) for x in r.all()]

    _sql_find_extendible_parents = """
-- find all extendible parent nodes
SELECT m.id as parent_id, m.depth, m.message_tree_id, COUNT(c.id) active_children_count
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id	-- all elements of message tree
    LEFT JOIN message c ON m.id = c.Id  -- child nodes
WHERE mts.active                        -- only consider active trees
    AND mts.state = :growing_state      -- message tree must be growing
    AND NOT m.deleted                   -- ignore deleted messages as parents
    AND m.depth < mts.max_depth         -- ignore leaf nodes as parents
    AND m.review_result                 -- parent node must have positive review
    AND NOT c.deleted                   -- don't count deleted children
    AND (c.review_result OR c.review_count < :num_reviews_reply) -- don't count children with negative review but count elements under review
GROUP BY m.id, m.depth, m.message_tree_id, mts.max_children_count
HAVING COUNT(c.id) < mts.max_children_count -- below maximum number of children
"""

    def query_extendible_parents(self) -> list[ExtendibleParentRow]:
        """Query parent messages that have not reached the maximum number of replies."""

        r = self.db.execute(
            text(self._sql_find_extendible_parents),
            {
                "growing_state": message_tree_state.State.GROWING,
                "num_reviews_reply": self.cfg.num_reviews_reply,
            },
        )
        return [ExtendibleParentRow.from_orm(x) for x in r.all()]

    _sql_find_extendible_trees = f"""
-- find extendible trees
SELECT m.message_tree_id, mts.goal_tree_size, COUNT(m.id) AS tree_size
FROM (
        SELECT DISTINCT message_tree_id FROM ({_sql_find_extendible_parents}) extendible_parents
    ) trees LEFT JOIN message_tree_state mts ON trees.message_tree_id = mts.message_tree_id
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE NOT m.deleted
    AND (
        m.parent_id IS NOT NULL AND (m.review_result OR m.review_count < :num_reviews_reply) -- children
        OR m.parent_id IS NULL AND m.review_result -- prompts (root nodes) must have positive review
    )
GROUP BY m.message_tree_id, mts.goal_tree_size
HAVING COUNT(m.id) < mts.goal_tree_size
"""

    def query_extendible_trees(self) -> list[ActiveTreeSizeRow]:
        """Query size of active message trees in growing state."""

        r = self.db.execute(
            text(self._sql_find_extendible_trees),
            {
                "growing_state": message_tree_state.State.GROWING,
                "num_reviews_reply": self.cfg.num_reviews_reply,
            },
        )
        return [ActiveTreeSizeRow.from_orm(x) for x in r.all()]

    _sql_get_tree_size = """
SELECT mts.message_tree_id, mts.goal_tree_size, COUNT(m.id) AS tree_size
FROM message_tree_state mts
    LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active
    AND NOT m.deleted
    AND m.review_result
    AND mts.message_tree_id = :message_tree_id
GROUP BY mts.message_tree_id, mts.goal_tree_size
"""

    def query_tree_size(self, message_tree_id: UUID) -> ActiveTreeSizeRow:
        """Returns the number of reviewed not deleted messages in the message tree."""
        r = self.db.execute(text(self._sql_get_tree_size), {"message_tree_id": message_tree_id})
        return ActiveTreeSizeRow.from_orm(r.one())

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

    _sql_find_tree_ranking_results = """
-- get all ranking results of completed tasks for all parents with >=2 children
SELECT p.parent_id, mr.* FROM
(
    -- find parents with > 1 children
    SELECT m.parent_id, m.message_tree_id, COUNT(m.id) children_count
    FROM message_tree_state mts
       LEFT JOIN message m ON mts.message_tree_id = m.message_tree_id
    WHERE m.review_result                  -- must be reviewed
       AND NOT m.deleted                   -- not deleted
       AND m.parent_id IS NOT NULL         -- ignore initial prompts
      AND mts.message_tree_id = :message_tree_id
    GROUP BY m.parent_id, m.message_tree_id
    HAVING COUNT(m.id) > 1
) as p
LEFT JOIN task t ON p.parent_id = t.parent_message_id AND t.done AND (t.payload_type = 'RankPrompterRepliesPayload' OR t.payload_type = 'RankAssistantRepliesPayload')
LEFT JOIN message_reaction mr ON mr.task_id = t.id AND mr.payload_type = 'RankingReactionPayload'
"""

    def query_tree_ranking_results(self, message_tree_id: UUID) -> dict[UUID, list[MessageReaction]]:
        """Finds all completed ranking restuls for a message_tree"""
        r = self.db.execute(
            text(self._sql_find_tree_ranking_results),
            {"message_tree_id": message_tree_id},
        )

        rankings_by_message = {}
        for x in r.all():
            parent_id = x["parent_id"]
            if parent_id not in rankings_by_message:
                rankings_by_message[parent_id] = []
            if x["task_id"]:
                rankings_by_message[parent_id].append(MessageReaction.from_orm(x))
        return rankings_by_message

    def ensure_tree_states(self):
        """Add message tree state rows for all root nodes (inital prompt messages)."""

        missing_tree_ids = self.query_misssing_tree_states()
        for id in missing_tree_ids:
            tree_size = self.db.query(func.count(Message.id)).filter(Message.message_tree_id == id).scalar()
            state = message_tree_state.State.INITIAL_PROMPT_REVIEW
            if tree_size > 1:
                state = message_tree_state.State.GROWING
                logger.info(f"Inserting missing message tree state for message: {id} ({tree_size=}, {state=})")
            self._insert_default_state(id, state=state)
        self.db.commit()

    def query_num_active_trees(self) -> int:
        query = self.db.query(func.count(MessageTreeState.message_tree_id)).filter(MessageTreeState.active)
        return query.scalar()

    def query_reviews_for_message(self, message_id: UUID) -> list[TextLabels]:
        sql_qry = """
SELECT tl.*
FROM task t
    INNER JOIN text_labels tl ON tl.id = t.id
WHERE t.done = TRUE
    AND tl.message_id = :message_id
"""
        r = self.db.execute(text(sql_qry), {"message_id": message_id})
        return [TextLabels.from_orm(x) for x in r.all()]

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
        )

        self.db.add(model)
        return model

    def _insert_default_state(
        self,
        root_message_id: UUID,
        state: message_tree_state.State = message_tree_state.State.INITIAL_PROMPT_REVIEW,
    ) -> MessageTreeState:
        return self._insert_tree_state(
            root_message_id=root_message_id,
            goal_tree_size=self.cfg.goal_tree_size,
            max_depth=self.cfg.max_tree_depth,
            max_children_count=self.cfg.max_children_count,
            state=state,
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
        tm.ensure_tree_states()

        print("query_num_active_trees", tm.query_num_active_trees())
        print("query_incomplete_rankings", tm.query_incomplete_rankings())
        print("query_incomplete_reply_reviews", tm.query_replies_need_review())
        print("query_incomplete_initial_prompt_reviews", tm.query_prompts_need_review())
        print("query_extendible_trees", tm.query_extendible_trees())
        print("query_extendible_parents", tm.query_extendible_parents())

        print("next_task:", tm.next_task())

        print(
            ".query_tree_ranking_results", tm.query_tree_ranking_results(UUID("2ac20d38-6650-43aa-8bb3-f61080c0d921"))
        )
