import json
import random
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from itertools import groupby

import numpy as np
import pydantic
from loguru import logger
from oasst_backend.utils import tree_export
from oasst_backend.api.v1.utils import prepare_conversation, prepare_conversation_message_list
from oasst_backend.config import TreeManagerConfiguration, settings
from oasst_backend.models import Message, MessageReaction, MessageTreeState, Task, TextLabels, User, message_tree_state
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.utils.database_utils import CommitMode, async_managed_tx_method, managed_tx_method
from oasst_backend.utils.hugging_face import HfClassificationModel, HfEmbeddingModel, HfUrl, HuggingFaceAPI
from oasst_backend.utils.ranking import ranked_pairs
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session, func, not_, text, update
from sqlalchemy.sql import text
from fastapi.encoders import jsonable_encoder


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
    parent_role: str
    depth: int
    message_tree_id: UUID
    active_children_count: int

    class Config:
        orm_mode = True


class IncompleteRankingsRow(pydantic.BaseModel):
    parent_id: UUID
    role: str
    children_count: int
    child_min_ranking_count: int

    class Config:
        orm_mode = True


class TreeMessageCountStats(pydantic.BaseModel):
    message_tree_id: UUID
    state: str
    depth: int
    oldest: datetime
    youngest: datetime
    count: int
    goal_tree_size: int

    @property
    def completed(self) -> int:
        return self.count / self.goal_tree_size


class TreeManagerStats(pydantic.BaseModel):
    state_counts: dict[str, int]
    message_counts: list[TreeMessageCountStats]


class TreeManager:
    _all_text_labels = list(map(lambda x: x.value, protocol_schema.TextLabel))

    def __init__(
        self,
        db: Session,
        prompt_repository: PromptRepository,
        cfg: Optional[TreeManagerConfiguration] = None,
    ):
        self.db = db
        self.cfg = cfg or settings.tree_manager
        self.pr = prompt_repository

    def _random_task_selection(
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
            f"TreeManager._random_task_selection({num_ranking_tasks=}, {num_replies_need_review=}, "
            f"{num_prompts_need_review=}, {num_missing_prompts=}, {num_missing_replies=})"
        )

        task_type = TaskType.NONE
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
        if weight_sum > 1e-8:
            task_weights = task_weights / weight_sum
            task_type = TaskType(np.random.choice(a=len(task_weights), p=task_weights))

        logger.debug(f"Selected {task_type=}")
        return task_type

    def _determine_task_availability_internal(
        self,
        num_active_trees: int,
        extendible_parents: list[ExtendibleParentRow],
        prompts_need_review: list[Message],
        replies_need_review: list[Message],
        incomplete_rankings: list[IncompleteRankingsRow],
    ) -> dict[protocol_schema.TaskRequestType, int]:
        task_count_by_type: dict[protocol_schema.TaskRequestType, int] = {t: 0 for t in protocol_schema.TaskRequestType}

        num_missing_prompts = max(0, self.cfg.max_active_trees - num_active_trees)
        task_count_by_type[protocol_schema.TaskRequestType.initial_prompt] = num_missing_prompts

        task_count_by_type[protocol_schema.TaskRequestType.prompter_reply] = len(
            list(filter(lambda x: x.parent_role == "assistant", extendible_parents))
        )
        task_count_by_type[protocol_schema.TaskRequestType.assistant_reply] = len(
            list(filter(lambda x: x.parent_role == "prompter", extendible_parents))
        )

        task_count_by_type[protocol_schema.TaskRequestType.label_initial_prompt] = len(prompts_need_review)
        task_count_by_type[protocol_schema.TaskRequestType.label_assistant_reply] = len(
            list(filter(lambda m: m.role == "assistant", replies_need_review))
        )
        task_count_by_type[protocol_schema.TaskRequestType.label_prompter_reply] = len(
            list(filter(lambda m: m.role == "prompter", replies_need_review))
        )

        if self.cfg.rank_prompter_replies:
            task_count_by_type[protocol_schema.TaskRequestType.rank_prompter_replies] = len(
                list(filter(lambda r: r.role == "prompter", incomplete_rankings))
            )

        task_count_by_type[protocol_schema.TaskRequestType.rank_assistant_replies] = len(
            list(filter(lambda r: r.role == "assistant", incomplete_rankings))
        )

        task_count_by_type[protocol_schema.TaskRequestType.random] = sum(
            task_count_by_type[t] for t in protocol_schema.TaskRequestType if t in task_count_by_type
        )

        return task_count_by_type

    def determine_task_availability(self, lang: str) -> dict[protocol_schema.TaskRequestType, int]:
        self.pr.ensure_user_is_enabled()

        if not lang:
            lang = "en"
            logger.warning("Task availability request without lang tag received, assuming lang='en'.")

        num_active_trees = self.query_num_active_trees(lang=lang)
        extendible_parents = self.query_extendible_parents(lang=lang)
        prompts_need_review = self.query_prompts_need_review(lang=lang)
        replies_need_review = self.query_replies_need_review(lang=lang)
        incomplete_rankings = self.query_incomplete_rankings(lang=lang)

        return self._determine_task_availability_internal(
            num_active_trees=num_active_trees,
            extendible_parents=extendible_parents,
            prompts_need_review=prompts_need_review,
            replies_need_review=replies_need_review,
            incomplete_rankings=incomplete_rankings,
        )

    def next_task(
        self,
        desired_task_type: protocol_schema.TaskRequestType = protocol_schema.TaskRequestType.random,
        lang: str = "en",
    ) -> Tuple[protocol_schema.Task, Optional[UUID], Optional[UUID]]:

        logger.debug(f"TreeManager.next_task({desired_task_type=}, {lang=})")

        self.pr.ensure_user_is_enabled()

        if not lang:
            lang = "en"
            logger.warning("Task request without lang tag received, assuming 'en'.")

        num_active_trees = self.query_num_active_trees(lang=lang)
        prompts_need_review = self.query_prompts_need_review(lang=lang)
        replies_need_review = self.query_replies_need_review(lang=lang)
        extendible_parents = self.query_extendible_parents(lang=lang)

        incomplete_rankings = self.query_incomplete_rankings(lang=lang)
        if not self.cfg.rank_prompter_replies:
            incomplete_rankings = list(filter(lambda r: r.role == "assistant", incomplete_rankings))

        active_tree_sizes = self.query_extendible_trees(lang=lang)

        # determine type of task to generate
        num_missing_replies = sum(x.remaining_messages for x in active_tree_sizes)

        task_role = TaskRole.ANY
        if desired_task_type == protocol_schema.TaskRequestType.random:
            task_type = self._random_task_selection(
                num_ranking_tasks=len(incomplete_rankings),
                num_replies_need_review=len(replies_need_review),
                num_prompts_need_review=len(prompts_need_review),
                num_missing_prompts=max(0, self.cfg.max_active_trees - num_active_trees),
                num_missing_replies=num_missing_replies,
            )

            if task_type == TaskType.NONE:
                raise OasstError(
                    f"No tasks of type '{protocol_schema.TaskRequestType.random.value}' are currently available.",
                    OasstErrorCode.TASK_REQUESTED_TYPE_NOT_AVAILABLE,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
        else:
            task_count_by_type = self._determine_task_availability_internal(
                num_active_trees=num_active_trees,
                extendible_parents=extendible_parents,
                prompts_need_review=prompts_need_review,
                replies_need_review=replies_need_review,
                incomplete_rankings=incomplete_rankings,
            )

            available_count = task_count_by_type.get(desired_task_type)
            if not available_count:
                raise OasstError(
                    f"No tasks of type '{desired_task_type.value}' are currently available.",
                    OasstErrorCode.TASK_REQUESTED_TYPE_NOT_AVAILABLE,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )

            task_type_role_map = {
                protocol_schema.TaskRequestType.initial_prompt: (TaskType.PROMPT, TaskRole.ANY),
                protocol_schema.TaskRequestType.prompter_reply: (TaskType.REPLY, TaskRole.PROMPTER),
                protocol_schema.TaskRequestType.assistant_reply: (TaskType.REPLY, TaskRole.ASSISTANT),
                protocol_schema.TaskRequestType.rank_prompter_replies: (TaskType.RANKING, TaskRole.PROMPTER),
                protocol_schema.TaskRequestType.rank_assistant_replies: (TaskType.RANKING, TaskRole.ASSISTANT),
                protocol_schema.TaskRequestType.label_initial_prompt: (TaskType.LABEL_PROMPT, TaskRole.ANY),
                protocol_schema.TaskRequestType.label_assistant_reply: (TaskType.LABEL_REPLY, TaskRole.ASSISTANT),
                protocol_schema.TaskRequestType.label_prompter_reply: (TaskType.LABEL_REPLY, TaskRole.PROMPTER),
            }

            task_type, task_role = task_type_role_map[desired_task_type]

        message_tree_id = None
        parent_message_id = None

        logger.debug(f"selected {task_type=}")
        match task_type:
            case TaskType.RANKING:
                if task_role == TaskRole.PROMPTER:
                    incomplete_rankings = list(filter(lambda m: m.role == "prompter", incomplete_rankings))
                elif task_role == TaskRole.ASSISTANT:
                    incomplete_rankings = list(filter(lambda m: m.role == "assistant", incomplete_rankings))

                if len(incomplete_rankings) > 0:
                    ranking_parent_id = random.choice(incomplete_rankings).parent_id

                    messages = self.pr.fetch_message_conversation(ranking_parent_id)
                    assert len(messages) > 0 and messages[-1].id == ranking_parent_id
                    ranking_parent = messages[-1]
                    assert not ranking_parent.deleted and ranking_parent.review_result
                    conversation = prepare_conversation(messages)
                    replies = self.pr.fetch_message_children(ranking_parent_id, reviewed=True, exclude_deleted=True)

                    assert len(replies) > 1
                    random.shuffle(replies)  # hand out replies in random order
                    reply_messages = prepare_conversation_message_list(replies)
                    replies = [p.text for p in replies]

                    if messages[-1].role == "assistant":
                        logger.info("Generating a RankPrompterRepliesTask.")
                        task = protocol_schema.RankPrompterRepliesTask(
                            conversation=conversation,
                            replies=replies,
                            reply_messages=reply_messages,
                            ranking_parent_id=ranking_parent.id,
                            message_tree_id=ranking_parent.message_tree_id,
                        )
                    else:
                        logger.info("Generating a RankAssistantRepliesTask.")
                        task = protocol_schema.RankAssistantRepliesTask(
                            conversation=conversation,
                            replies=replies,
                            reply_messages=reply_messages,
                            ranking_parent_id=ranking_parent.id,
                            message_tree_id=ranking_parent.message_tree_id,
                        )

                    parent_message_id = ranking_parent_id
                    message_tree_id = messages[-1].message_tree_id

            case TaskType.LABEL_REPLY:
                if task_role == TaskRole.PROMPTER:
                    replies_need_review = list(filter(lambda m: m.role == "prompter", replies_need_review))
                elif task_role == TaskRole.ASSISTANT:
                    replies_need_review = list(filter(lambda m: m.role == "assistant", replies_need_review))

                if len(replies_need_review) > 0:
                    random_reply_message = random.choice(replies_need_review)
                    messages = self.pr.fetch_message_conversation(random_reply_message)

                    conversation = prepare_conversation(messages[:-1])
                    message = messages[-1]

                    self.cfg.p_full_labeling_review_reply_prompter: float = 0.1

                    label_mode = protocol_schema.LabelTaskMode.full
                    valid_labels = self._all_text_labels

                    if message.role == "assistant":
                        if (
                            desired_task_type == protocol_schema.TaskRequestType.random
                            and random.random() > self.cfg.p_full_labeling_review_reply_assistant
                        ):
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
                        if (
                            desired_task_type == protocol_schema.TaskRequestType.random
                            and random.random() > self.cfg.p_full_labeling_review_reply_prompter
                        ):
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
                if task_role == TaskRole.PROMPTER:
                    extendible_parents = list(filter(lambda x: x.parent_role == "assistant", extendible_parents))
                elif task_role == TaskRole.ASSISTANT:
                    extendible_parents = list(filter(lambda x: x.parent_role == "prompter", extendible_parents))

                if len(extendible_parents) > 0:
                    random_parent = random.choice(extendible_parents)

                    # fetch random conversation to extend
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
                message = random.choice(prompts_need_review)

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

        if task is None:
            raise OasstError(
                f"No task of type '{desired_task_type.value}' is currently available.",
                OasstErrorCode.TASK_REQUESTED_TYPE_NOT_AVAILABLE,
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        logger.info(f"Generated {task=}.")

        return task, message_tree_id, parent_message_id

    @async_managed_tx_method(CommitMode.COMMIT)
    async def handle_interaction(self, interaction: protocol_schema.AnyInteraction) -> protocol_schema.Task:
        pr = self.pr
        pr.ensure_user_is_enabled()
        match type(interaction):
            case protocol_schema.TextReplyToMessage:
                logger.info(
                    f"Frontend reports text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                )

                # ensure message size is below the predefined limit
                if len(interaction.text) > settings.MESSAGE_SIZE_LIMIT:
                    logger.error(
                        f"Message size {len(interaction.text)=} exceeds size limit of {settings.MESSAGE_SIZE_LIMIT=}."
                    )
                    raise OasstError("Message size too long.", OasstErrorCode.TASK_MESSAGE_TOO_LONG)

                # here we store the text reply in the database
                message = pr.store_text_reply(
                    text=interaction.text,
                    lang=interaction.lang,
                    frontend_message_id=interaction.message_id,
                    user_frontend_message_id=interaction.user_message_id,
                )

                if not message.parent_id:
                    logger.info(f"TreeManager: Inserting new tree state for initial prompt {message.id=}")
                    self._insert_default_state(message.id)

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

                ok, rankings_by_message = self.check_condition_for_scoring_state(task.message_tree_id)
                self.update_message_ranks(task.message_tree_id, rankings_by_message)

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
                            logger.info(
                                f"Reply message message accepted: {msg.id=}, {acceptance_score=}, {len(reviews)=}"
                            )

                    self.check_condition_for_ranking_state(msg.message_tree_id)

            case _:
                raise OasstError("Invalid response type.", OasstErrorCode.TASK_INVALID_RESPONSE_TYPE)

        return protocol_schema.TaskDone()

    @managed_tx_method(CommitMode.FLUSH)
    def _enter_state(self, mts: MessageTreeState, state: message_tree_state.State):
        assert mts and mts.active

        is_terminal = state in message_tree_state.TERMINAL_STATES

        if is_terminal:
            mts.active = False
        mts.state = state.value
        self.db.add(mts)

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

    def check_condition_for_scoring_state(
        self, message_tree_id: UUID
    ) -> Tuple[bool, dict[UUID, list[MessageReaction]]]:
        logger.debug(f"check_condition_for_scoring_state({message_tree_id=})")

        mts = self.pr.fetch_tree_state(message_tree_id)
        if not mts.active or mts.state != message_tree_state.State.RANKING:
            logger.debug(f"False {mts.active=}, {mts.state=}")
            return False, None

        ranking_role_filter = None if self.cfg.rank_prompter_replies else "assistant"
        rankings_by_message = self.query_tree_ranking_results(message_tree_id, role_filter=ranking_role_filter)
        for parent_msg_id, ranking in rankings_by_message.items():
            if len(ranking) < self.cfg.num_required_rankings:
                logger.debug(f"False {parent_msg_id=} {len(ranking)=}")
                return False, None

        self._enter_state(mts, message_tree_state.State.READY_FOR_SCORING)
        return True, rankings_by_message

    def update_message_ranks(self, message_tree_id: UUID, rankings_by_message: Dict[int, int]) -> bool:

        mts = self.pr.fetch_tree_state(message_tree_id)
        # check state, allow retry if in SCORING_FAILED state
        if mts.state not in (message_tree_state.State.READY_FOR_SCORING, message_tree_state.State.SCORING_FAILED):
            logger.debug(f"False {mts.active=}, {mts.state=}")
            return False

        try:
            for rankings in rankings_by_message.values():
                sorted_messages = []
                for msg_reaction in rankings:
                    sorted_messages.append(msg_reaction.payload.payload.ranked_message_ids)
                logger.debug(f"SORTED MESSAGE {sorted_messages}")
                consensus = ranked_pairs(sorted_messages)
                logger.debug(f"CONSENSUS: {consensus}\n\n")
                for rank, message_id in enumerate(consensus):
                    # set rank for each message_id for Message rows
                    msg = self.pr.fetch_message(message_id=message_id, fail_if_missing=True)
                    msg.rank = rank
                    self.db.add(msg)

        except Exception:
            logger.exception(f"update_message_ranks({message_tree_id=}) failed")
            self._enter_state(mts, message_tree_state.State.SCORING_FAILED)
            return False

        self._enter_state(mts, message_tree_state.State.READY_FOR_EXPORT)
        return True

    def _calculate_acceptance(self, labels: list[TextLabels]):
        # calculate acceptance based on spam label
        return np.mean([1 - l.labels[protocol_schema.TextLabel.spam] for l in labels])

    def query_prompts_need_review(self, lang: str) -> list[Message]:
        """
        Select initial prompt messages with less then required rankings in active message tree
        (active == True in message_tree_state)
        """

        qry = (
            self.db.query(Message)
            .select_from(MessageTreeState)
            .join(Message, MessageTreeState.message_tree_id == Message.message_tree_id)
            .filter(
                MessageTreeState.active,
                MessageTreeState.state == message_tree_state.State.INITIAL_PROMPT_REVIEW,
                not_(Message.review_result),
                not_(Message.deleted),
                Message.review_count < self.cfg.num_reviews_initial_prompt,
                Message.parent_id.is_(None),
                Message.lang == lang,
            )
        )

        if not settings.DEBUG_ALLOW_SELF_LABELING:
            qry = qry.filter(Message.user_id != self.pr.user_id)

        return qry.all()

    def query_replies_need_review(self, lang: str) -> list[Message]:
        """
        Select child messages (parent_id IS NOT NULL) with less then required rankings
        in active message tree (active == True in message_tree_state)
        """

        qry = (
            self.db.query(Message)
            .select_from(MessageTreeState)
            .join(Message, MessageTreeState.message_tree_id == Message.message_tree_id)
            .filter(
                MessageTreeState.active,
                MessageTreeState.state == message_tree_state.State.GROWING,
                not_(Message.review_result),
                not_(Message.deleted),
                Message.review_count < self.cfg.num_reviews_reply,
                Message.parent_id.is_not(None),
                Message.lang == lang,
            )
        )

        if not settings.DEBUG_ALLOW_SELF_LABELING:
            qry = qry.filter(Message.user_id != self.pr.user_id)

        return qry.all()

    _sql_find_incomplete_rankings = """
-- find incomplete rankings
SELECT m.parent_id, m.role, COUNT(m.id) children_count, MIN(m.ranking_count) child_min_ranking_count,
    COUNT(m.id) FILTER (WHERE m.ranking_count >= :num_required_rankings) as completed_rankings
FROM message_tree_state mts
    INNER JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE mts.active                        -- only consider active trees
    AND mts.state = :ranking_state      -- message tree must be in ranking state
    AND m.review_result                 -- must be reviewed
    AND m.lang = :lang                  -- matches lang
    AND NOT m.deleted                   -- not deleted
    AND m.parent_id IS NOT NULL         -- ignore initial prompts
GROUP BY m.parent_id, m.role
HAVING COUNT(m.id) > 1 and MIN(m.ranking_count) < :num_required_rankings
"""

    def query_incomplete_rankings(self, lang: str) -> list[IncompleteRankingsRow]:
        """Query parents which have childern that need further rankings"""

        r = self.db.execute(
            text(self._sql_find_incomplete_rankings),
            {
                "num_required_rankings": self.cfg.num_required_rankings,
                "ranking_state": message_tree_state.State.RANKING,
                "lang": lang,
            },
        )
        return [IncompleteRankingsRow.from_orm(x) for x in r.all()]

    _sql_find_extendible_parents = """
-- find all extendible parent nodes
SELECT m.id as parent_id, m.role as parent_role, m.depth, m.message_tree_id, COUNT(c.id) active_children_count
FROM message_tree_state mts
    INNER JOIN message m ON mts.message_tree_id = m.message_tree_id	-- all elements of message tree
    LEFT JOIN message c ON m.id = c.parent_id  -- child nodes
WHERE mts.active                        -- only consider active trees
    AND mts.state = :growing_state      -- message tree must be growing
    AND NOT m.deleted                   -- ignore deleted messages as parents
    AND m.depth < mts.max_depth         -- ignore leaf nodes as parents
    AND m.review_result                 -- parent node must have positive review
    AND m.lang = :lang                  -- parent matches lang
    AND NOT coalesce(c.deleted, FALSE)  -- don't count deleted children
    AND (c.review_result OR coalesce(c.review_count, 0) < :num_reviews_reply) -- don't count children with negative review but count elements under review
GROUP BY m.id, m.role, m.depth, m.message_tree_id, mts.max_children_count
HAVING COUNT(c.id) < mts.max_children_count -- below maximum number of children
"""

    def query_extendible_parents(self, lang: str) -> list[ExtendibleParentRow]:
        """Query parent messages that have not reached the maximum number of replies."""

        r = self.db.execute(
            text(self._sql_find_extendible_parents),
            {
                "growing_state": message_tree_state.State.GROWING,
                "num_reviews_reply": self.cfg.num_reviews_reply,
                "lang": lang,
            },
        )
        return [ExtendibleParentRow.from_orm(x) for x in r.all()]

    _sql_find_extendible_trees = f"""
-- find extendible trees
SELECT m.message_tree_id, mts.goal_tree_size, COUNT(m.id) AS tree_size
FROM (
        SELECT DISTINCT message_tree_id FROM ({_sql_find_extendible_parents}) extendible_parents
    ) trees INNER JOIN message_tree_state mts ON trees.message_tree_id = mts.message_tree_id
    INNER JOIN message m ON mts.message_tree_id = m.message_tree_id
WHERE NOT m.deleted
    AND (
        m.parent_id IS NOT NULL AND (m.review_result OR m.review_count < :num_reviews_reply) -- children
        OR m.parent_id IS NULL AND m.review_result -- prompts (root nodes) must have positive review
    )
GROUP BY m.message_tree_id, mts.goal_tree_size
HAVING COUNT(m.id) < mts.goal_tree_size
"""

    def query_extendible_trees(self, lang: str) -> list[ActiveTreeSizeRow]:
        """Query size of active message trees in growing state."""

        r = self.db.execute(
            text(self._sql_find_extendible_trees),
            {
                "growing_state": message_tree_state.State.GROWING,
                "num_reviews_reply": self.cfg.num_reviews_reply,
                "lang": lang,
            },
        )
        return [ActiveTreeSizeRow.from_orm(x) for x in r.all()]

    def query_tree_size(self, message_tree_id: UUID) -> ActiveTreeSizeRow:
        """Returns the number of reviewed not deleted messages in the message tree."""

        qry = (
            self.db.query(
                MessageTreeState.message_tree_id.label("message_tree_id"),
                MessageTreeState.goal_tree_size.label("goal_tree_size"),
                func.count(Message.id).label("tree_size"),
            )
            .select_from(MessageTreeState)
            .outerjoin(Message, MessageTreeState.message_tree_id == Message.message_tree_id)
            .filter(
                MessageTreeState.active,
                not_(Message.deleted),
                Message.review_result,
                MessageTreeState.message_tree_id == message_tree_id,
            )
            .group_by(MessageTreeState.message_tree_id, MessageTreeState.goal_tree_size)
        )

        return ActiveTreeSizeRow.from_orm(qry.one())

    def query_misssing_tree_states(self) -> list[UUID]:
        """Find all initial prompt messages that have no associated message tree state"""
        qry_missing_tree_states = (
            self.db.query(Message.id)
            .outerjoin(MessageTreeState, Message.message_tree_id == MessageTreeState.message_tree_id)
            .filter(
                Message.parent_id.is_(None),
                Message.message_tree_id == Message.id,
                MessageTreeState.message_tree_id.is_(None),
            )
        )

        return [m.id for m in qry_missing_tree_states.all()]

    _sql_find_tree_ranking_results = """
-- get all ranking results of completed tasks for all parents with >= 2 children
SELECT p.parent_id, mr.* FROM
(
    -- find parents with > 1 children
    SELECT m.parent_id, m.message_tree_id, COUNT(m.id) children_count
    FROM message_tree_state mts
       INNER JOIN message m ON mts.message_tree_id = m.message_tree_id
    WHERE m.review_result                  -- must be reviewed
       AND NOT m.deleted                   -- not deleted
       AND m.parent_id IS NOT NULL         -- ignore initial prompts
       AND (:role IS NULL OR m.role = :role) -- children with matching role
       AND mts.message_tree_id = :message_tree_id
    GROUP BY m.parent_id, m.message_tree_id
    HAVING COUNT(m.id) > 1
) as p
INNER JOIN task t ON p.parent_id = t.parent_message_id AND t.done AND (t.payload_type = 'RankPrompterRepliesPayload' OR t.payload_type = 'RankAssistantRepliesPayload')
INNER JOIN message_reaction mr ON mr.task_id = t.id AND mr.payload_type = 'RankingReactionPayload'
"""

    def query_tree_ranking_results(
        self,
        message_tree_id: UUID,
        role_filter: str = "assistant",
    ) -> dict[UUID, list[MessageReaction]]:
        """Finds all completed ranking restuls for a message_tree"""

        assert role_filter in (None, "assistant", "prompter")

        r = self.db.execute(
            text(self._sql_find_tree_ranking_results),
            {
                "message_tree_id": message_tree_id,
                "role": role_filter,
            },
        )

        rankings_by_message = {}
        for x in r.all():
            parent_id = x["parent_id"]
            if parent_id not in rankings_by_message:
                rankings_by_message[parent_id] = []
            if x["task_id"]:
                rankings_by_message[parent_id].append(MessageReaction.from_orm(x))
        return rankings_by_message

    @managed_tx_method(CommitMode.COMMIT)
    def ensure_tree_states(self):
        """Add message tree state rows for all root nodes (inital prompt messages)."""

        missing_tree_ids = self.query_misssing_tree_states()
        for id in missing_tree_ids:
            tree_size = self.db.query(func.count(Message.id)).filter(Message.message_tree_id == id).scalar()
            state = message_tree_state.State.INITIAL_PROMPT_REVIEW
            if tree_size > 1:
                state = message_tree_state.State.GROWING
                logger.info(f"Inserting missing message tree state for message: {id} ({tree_size=}, {state=:s})")
            self._insert_default_state(id, state=state)

    def query_num_active_trees(self, lang: str) -> int:
        query = (
            self.db.query(func.count(MessageTreeState.message_tree_id))
            .join(Message, MessageTreeState.message_tree_id == Message.id)
            .filter(MessageTreeState.active, Message.lang == lang)
        )
        return query.scalar()

    def query_reviews_for_message(self, message_id: UUID) -> list[TextLabels]:
        qry = (
            self.db.query(TextLabels)
            .select_from(Task)
            .join(TextLabels, Task.id == TextLabels.id)
            .filter(Task.done, TextLabels.message_id == message_id)
        )
        return qry.all()

    @managed_tx_method(CommitMode.FLUSH)
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

    @managed_tx_method(CommitMode.FLUSH)
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

    def tree_counts_by_state(self) -> dict[str, int]:
        qry = self.db.query(
            MessageTreeState.state, func.count(MessageTreeState.message_tree_id).label("count")
        ).group_by(MessageTreeState.state)
        return {x["state"]: x["count"] for x in qry}

    def tree_message_count_stats(self, only_active: bool = True) -> list[TreeMessageCountStats]:
        qry = (
            self.db.query(
                MessageTreeState.message_tree_id,
                func.max(Message.depth).label("depth"),
                func.min(Message.created_date).label("oldest"),
                func.max(Message.created_date).label("youngest"),
                func.count(Message.id).label("count"),
                MessageTreeState.goal_tree_size,
                MessageTreeState.state,
            )
            .select_from(MessageTreeState)
            .join(Message, MessageTreeState.message_tree_id == Message.message_tree_id)
            .filter(not_(Message.deleted))
            .group_by(MessageTreeState.message_tree_id)
        )

        if only_active:
            qry = qry.filter(MessageTreeState.active)

        return [TreeMessageCountStats(**x) for x in qry]

    def stats(self) -> TreeManagerStats:
        return TreeManagerStats(
            state_counts=self.tree_counts_by_state(),
            message_counts=self.tree_message_count_stats(only_active=True),
        )

    def get_user_messages_by_tree(
        self,
        user_id: UUID,
        min_date: datetime = None,
        max_date: datetime = None,
    ) -> Tuple[dict[UUID, list[Message]], list[Message]]:
        """Returns a dict with replies by tree (excluding initial prompts) and list of initial prompts
        associated with user_id."""

        # query all messages of the user
        qry = self.db.query(Message).filter(Message.user_id == user_id)
        if min_date:
            qry = qry.filter(Message.created_date >= min_date)
        if max_date:
            qry = qry.filter(Message.created_date <= max_date)

        prompts: list[Message] = []
        replies_by_tree: dict[UUID, list[Message]] = {}

        # walk over result set and distinguish between initial prompts and replies
        for m in qry:
            m: Message

            if m.message_tree_id == m.id:
                prompts.append(m)
            else:
                message_list = replies_by_tree.get(m.message_tree_id)
                if message_list is None:
                    message_list = [m]
                    replies_by_tree[m.message_tree_id] = message_list
                else:
                    message_list.append(m)

        return replies_by_tree, prompts

    def _purge_message_internal(self, message_id: UUID) -> None:
        """This internal function deletes a single message. It does not take care of
        descendants, children_count in parent etc."""

        sql_purge_message = """
DELETE FROM journal j USING message m WHERE j.message_id = :message_id;
DELETE FROM message_embedding e WHERE e.message_id = :message_id;
DELETE FROM message_toxicity t WHERE t.message_id = :message_id;
DELETE FROM text_labels l WHERE l.message_id = :message_id;
-- delete all ranking results that contain message
DELETE FROM message_reaction r WHERE r.payload_type = 'RankingReactionPayload' AND r.task_id IN (
        SELECT t.id FROM message m
            JOIN task t ON m.parent_id = t.parent_message_id
        WHERE m.id = :message_id);
-- delete task which inserted message
DELETE FROM task t using message m WHERE t.id = m.task_id AND m.id = :message_id;
DELETE FROM task t WHERE t.parent_message_id = :message_id;
DELETE FROM message WHERE id = :message_id;
"""
        r = self.db.execute(text(sql_purge_message), {"message_id": message_id})
        logger.debug(f"purge_message({message_id=}): {r.rowcount} rows.")

    def purge_message_tree(self, message_tree_id: UUID) -> None:
        sql_purge_message_tree = """
DELETE FROM journal j USING message m WHERE j.message_id = m.Id AND m.message_tree_id = :message_tree_id;
DELETE FROM message_embedding e USING message m WHERE e.message_id = m.Id AND m.message_tree_id = :message_tree_id;
DELETE FROM message_toxicity t USING message m WHERE t.message_id = m.Id AND m.message_tree_id = :message_tree_id;
DELETE FROM text_labels l USING message m WHERE l.message_id = m.Id AND m.message_tree_id = :message_tree_id;
DELETE FROM message_reaction r USING task t WHERE r.task_id = t.id AND t.message_tree_id = :message_tree_id;
DELETE FROM task t WHERE t.message_tree_id = :message_tree_id;
DELETE FROM message_tree_state WHERE message_tree_id = :message_tree_id;
DELETE FROM message WHERE message_tree_id = :message_tree_id;
"""
        r = self.db.execute(text(sql_purge_message_tree), {"message_tree_id": message_tree_id})
        logger.debug(f"purge_message_tree({message_tree_id=}) {r.rowcount} rows.")

    @managed_tx_method(CommitMode.FLUSH)
    def purge_user_messages(
        self,
        user_id: UUID,
        purge_initial_prompts: bool = True,
        min_date: datetime = None,
        max_date: datetime = None,
    ):

        # find all affected message trees
        replies_by_tree, prompts = self.get_user_messages_by_tree(user_id, min_date, max_date)
        total_messages = sum(len(x) for x in replies_by_tree.values())
        logger.debug(f"found: {len(replies_by_tree)} trees; {len(prompts)} prompts; {total_messages} messages;")

        # remove all trees based on inital prompts of the user
        if purge_initial_prompts:
            for p in prompts:
                self.purge_message_tree(p.message_tree_id)
                if p.message_tree_id in replies_by_tree:
                    del replies_by_tree[p.message_tree_id]

        # patch all affected message trees
        for tree_id, replies in replies_by_tree.items():
            bad_parent_ids = set(m.id for m in replies)
            logger.debug(f"patching tree {tree_id=}, {bad_parent_ids=}")

            tree_messages = self.pr.fetch_message_tree(tree_id, reviewed=False, include_deleted=True)
            logger.debug(f"{tree_id=}, {len(bad_parent_ids)=}, {len(tree_messages)=}")
            by_id = {m.id: m for m in tree_messages}

            def ancestor_ids(msg: Message) -> list[UUID]:
                t = []
                while msg.parent_id is not None:
                    msg = by_id[msg.parent_id]
                    t.append(msg.id)
                return t

            def is_descendant_of_deleted(m: Message) -> bool:
                if m.id in bad_parent_ids:
                    return True
                ancestors = ancestor_ids(m)
                if any(a in bad_parent_ids for a in ancestors):
                    return True
                return False

            # start with deepest messages first
            tree_messages.sort(key=lambda x: x.depth, reverse=True)
            for m in tree_messages:
                if is_descendant_of_deleted(m):
                    logger.debug(f"purging message: {m.id}")
                    self._purge_message_internal(m.id)

            # update childern counts
            self.pr.update_children_counts(m.message_tree_id)

            # reactivate tree
            logger.info(f"reactivating message tree {tree_id}")
            mts = self.pr.fetch_tree_state(tree_id)
            mts.active = True
            self._enter_state(mts, message_tree_state.State.INITIAL_PROMPT_REVIEW)
            self.check_condition_for_growing_state(tree_id)
            self.check_condition_for_ranking_state(tree_id)
            self.check_condition_for_scoring_state(tree_id)

    @managed_tx_method(CommitMode.FLUSH)
    def purge_user(self, user_id: UUID, ban: bool = True) -> None:
        self.purge_user_messages(user_id, purge_initial_prompts=True)

        # delete all remaining rows and ban user
        sql_purge_user = """
DELETE FROM journal WHERE user_id = :user_id;
DELETE FROM message_reaction WHERE user_id = :user_id;
DELETE FROM task WHERE user_id = :user_id;
DELETE FROM message WHERE user_id = :user_id;
DELETE FROM user_stats WHERE user_id = :user_id;
"""

        r = self.db.execute(text(sql_purge_user), {"user_id": user_id})
        logger.debug(f"purge_user({user_id=}): {r.rowcount} rows.")

        if ban:
            self.db.execute(update(User).filter(User.id == user_id).values(deleted=True, enabled=False))

    def export_trees_to_file(
        self,
        message_tree_ids: list[str],
        file=None,
        reviewed: bool = True,
        deleted: bool = False,
        use_compression: bool = True,
    ) -> None:
        for message_tree_id in message_tree_ids:
            messages: List[Message] = pr.fetch_message_tree(message_tree_id, reviewed, deleted)
            tree: tree_export.ExportMessageTree = tree_export.build_export_tree(message_tree_id, messages)
            if file:
                tree_export.write_tree_to_file(file, tree, use_compression)
            else:
                logger.info(json.dumps(jsonable_encoder(tree), indent=2))

    def export_all_ready_trees(
        self, file: str, reviewed: bool = True, deleted: bool = False, use_compression: bool = True
    ) -> None:
        message_tree_states: MessageTreeState = pr.fetch_message_trees_ready_for_export()
        message_tree_ids = [ms.message_tree_id for ms in message_tree_states]
        self.export_trees_to_file(message_tree_ids, file, reviewed, deleted, use_compression)

    def export_all_user_trees(
        self, user_id: str, file: str, reviewed: bool = True, deleted: bool = False, use_compression: bool = True
    ) -> None:
        messages = pr.fetch_user_message_trees(UUID(user_id))
        message_tree_ids = [ms.message_tree_id for ms in messages]
        self.export_trees_to_file(message_tree_ids, file, reviewed, deleted, use_compression)


if __name__ == "__main__":
    from oasst_backend.api.deps import create_api_client
    from oasst_backend.database import engine
    from oasst_backend.prompt_repository import PromptRepository

    with Session(engine) as db:
        api_client = create_api_client(session=db, description="test", frontend_type="bot")
        dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")

        pr = PromptRepository(db=db, api_client=api_client, client_user=dummy_user)

        cfg = TreeManagerConfiguration()
        tm = TreeManager(db, pr, cfg)
        tm.ensure_tree_states()

        tm.purge_user_messages(user_id=UUID("2ef9ad21-0dc5-442d-8750-6f7f1790723f"), purge_initial_prompts=False)
        # tm.purge_user(user_id=UUID("2ef9ad21-0dc5-442d-8750-6f7f1790723f"))
        # db.commit()

        # print("query_num_active_trees", tm.query_num_active_trees())
        # print("query_incomplete_rankings", tm.query_incomplete_rankings())
        # print("query_replies_need_review", tm.query_replies_need_review())
        # print("query_incomplete_reply_reviews", tm.query_replies_need_review())
        # print("query_incomplete_initial_prompt_reviews", tm.query_prompts_need_review())
        # print("query_extendible_trees", tm.query_extendible_trees())
        # print("query_extendible_parents", tm.query_extendible_parents())

        # print("next_task:", tm.next_task())

        # print(
        #     ".query_tree_ranking_results", tm.query_tree_ranking_results(UUID("2ac20d38-6650-43aa-8bb3-f61080c0d921"))
        # )

        print(tm.export_trees_to_file(message_tree_ids=["7e75fb38-e664-4e2b-817c-b9a0b01b0074"]))
