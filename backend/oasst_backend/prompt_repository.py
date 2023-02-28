import random
import re
from collections import defaultdict
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional
from uuid import UUID, uuid4

import oasst_backend.models.db_payload as db_payload
import sqlalchemy.dialects.postgresql as pg
from loguru import logger
from oasst_backend.api.deps import FrontendUserId
from oasst_backend.config import settings
from oasst_backend.journal_writer import JournalWriter
from oasst_backend.models import (
    ApiClient,
    FlaggedMessage,
    Message,
    MessageEmbedding,
    MessageEmoji,
    MessageReaction,
    MessageToxicity,
    MessageTreeState,
    Task,
    TextLabels,
    User,
    message_tree_state,
)
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_backend.task_repository import TaskRepository, validate_frontend_message_id
from oasst_backend.user_repository import UserRepository
from oasst_backend.utils.database_utils import CommitMode, managed_tx_method
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.schemas.protocol import SystemStats
from oasst_shared.utils import unaware_to_utc, utcnow
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import JSON, Session, and_, func, literal_column, not_, or_, text, update

_task_type_and_reaction = (
    (
        (db_payload.PrompterReplyPayload, db_payload.AssistantReplyPayload),
        protocol_schema.EmojiCode.skip_reply,
    ),
    (
        (db_payload.LabelInitialPromptPayload, db_payload.LabelConversationReplyPayload),
        protocol_schema.EmojiCode.skip_labeling,
    ),
    (
        (db_payload.RankInitialPromptsPayload, db_payload.RankConversationRepliesPayload),
        protocol_schema.EmojiCode.skip_ranking,
    ),
)


class PromptRepository:
    def __init__(
        self,
        db: Session,
        api_client: ApiClient,
        client_user: Optional[protocol_schema.User] = None,
        *,
        user_repository: Optional[UserRepository] = None,
        task_repository: Optional[TaskRepository] = None,
        user_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
        username: Optional[str] = None,
        frontend_user: Optional[FrontendUserId] = None,
    ):
        self.db = db
        self.api_client = api_client
        self.user_repository = user_repository or UserRepository(db, api_client)

        if frontend_user and not auth_method and not username:
            auth_method, username = frontend_user

        if user_id:
            self.user = self.user_repository.get_user(id=user_id)
        elif auth_method and username:
            self.user = self.user_repository.query_frontend_user(auth_method=auth_method, username=username)
        else:
            self.user = self.user_repository.lookup_client_user(client_user, create_missing=True)
        self.user_id = self.user.id if self.user else None
        logger.debug(f"PromptRepository(api_client_id={self.api_client.id}, {self.user_id=})")
        self.task_repository = task_repository or TaskRepository(
            db, api_client, client_user, user_repository=self.user_repository
        )
        self.journal = JournalWriter(db, api_client, self.user)

    def ensure_user_is_enabled(self):
        if self.user is None or self.user_id is None:
            raise OasstError("User required", OasstErrorCode.USER_NOT_SPECIFIED)

        if self.user.deleted or not self.user.enabled:
            raise OasstError("User account disabled", OasstErrorCode.USER_DISABLED, HTTPStatus.SERVICE_UNAVAILABLE)

        if self.user.tos_acceptance_date is None and not settings.DEBUG_IGNORE_TOS_ACCEPTANCE:
            raise OasstError(
                "User has not accepted terms of service.",
                OasstErrorCode.USER_HAS_NOT_ACCEPTED_TOS,
                HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS,
            )

    def fetch_message_by_frontend_message_id(self, frontend_message_id: str, fail_if_missing: bool = True) -> Message:
        validate_frontend_message_id(frontend_message_id)
        message: Message = (
            self.db.query(Message)
            .filter(Message.api_client_id == self.api_client.id, Message.frontend_message_id == frontend_message_id)
            .one_or_none()
        )
        if fail_if_missing and message is None:
            raise OasstError(
                f"Message with frontend_message_id {frontend_message_id} not found.",
                OasstErrorCode.MESSAGE_NOT_FOUND,
                HTTPStatus.NOT_FOUND,
            )
        return message

    @managed_tx_method(CommitMode.FLUSH)
    def insert_message(
        self,
        *,
        message_id: UUID,
        frontend_message_id: str,
        parent_id: UUID,
        message_tree_id: UUID,
        task_id: UUID,
        role: str,
        payload: db_payload.MessagePayload,
        lang: str,
        payload_type: str = None,
        depth: int = 0,
        review_count: int = 0,
        review_result: bool = None,
        deleted: bool = False,
    ) -> Message:
        if payload_type is None:
            if payload is None:
                payload_type = "null"
            else:
                payload_type = type(payload).__name__

        message = Message(
            id=message_id,
            parent_id=parent_id,
            message_tree_id=message_tree_id,
            task_id=task_id,
            user_id=self.user_id,
            role=role,
            frontend_message_id=frontend_message_id,
            api_client_id=self.api_client.id,
            payload_type=payload_type,
            payload=PayloadContainer(payload=payload),
            lang=lang,
            depth=depth,
            review_count=review_count,
            review_result=review_result,
            deleted=deleted,
        )
        self.db.add(message)
        return message

    def _validate_task(
        self,
        task: Task,
        *,
        task_id: Optional[UUID] = None,
        frontend_message_id: Optional[str] = None,
        check_ack: bool = True,
    ) -> Task:
        if task is None:
            if task_id:
                raise OasstError(f"Task for {task_id=} not found", OasstErrorCode.TASK_NOT_FOUND)
            if frontend_message_id:
                raise OasstError(f"Task for {frontend_message_id=} not found", OasstErrorCode.TASK_NOT_FOUND)
            raise OasstError("Task not found", OasstErrorCode.TASK_NOT_FOUND)

        if task.expired:
            raise OasstError("Task already expired.", OasstErrorCode.TASK_EXPIRED)
        if check_ack and not task.ack:
            raise OasstError("Task is not acknowledged.", OasstErrorCode.TASK_NOT_ACK)
        if task.done:
            raise OasstError("Task already done.", OasstErrorCode.TASK_ALREADY_DONE)

        if (not task.collective or task.user_id is None) and task.user_id != self.user_id:
            logger.warning(f"Task was assigned to a different user (expected: {task.user_id}; actual: {self.user_id}).")
            raise OasstError("Task was assigned to a different user.", OasstErrorCode.TASK_NOT_ASSIGNED_TO_USER)

        return task

    def fetch_tree_state(self, message_tree_id: UUID) -> MessageTreeState:
        return self.db.query(MessageTreeState).filter(MessageTreeState.message_tree_id == message_tree_id).one()

    @managed_tx_method(CommitMode.FLUSH)
    def store_text_reply(
        self,
        text: str,
        lang: str,
        frontend_message_id: str,
        user_frontend_message_id: str,
        review_count: int = 0,
        review_result: bool = None,
        check_tree_state: bool = True,
        check_duplicate: bool = True,
    ) -> Message:
        self.ensure_user_is_enabled()

        validate_frontend_message_id(frontend_message_id)
        validate_frontend_message_id(user_frontend_message_id)

        task = self.task_repository.fetch_task_by_frontend_message_id(frontend_message_id)
        self._validate_task(task)

        # If there's no parent message assume user started new conversation
        role: str = None
        depth: int = 0
        deleted: bool = False

        # reject whitespaces match with ^\s+$
        if re.match(r"^\s+$", text):
            raise OasstError("Message text is empty", OasstErrorCode.TASK_MESSAGE_TEXT_EMPTY)

        # ensure message size is below the predefined limit
        if len(text) > settings.MESSAGE_SIZE_LIMIT:
            logger.error(f"Message size {len(text)=} exceeds size limit of {settings.MESSAGE_SIZE_LIMIT=}.")
            raise OasstError("Message size too long.", OasstErrorCode.TASK_MESSAGE_TOO_LONG)

        if check_duplicate and self.check_users_recent_replies_for_duplicates(text):
            raise OasstError("User recent messages have duplicates", OasstErrorCode.TASK_MESSAGE_DUPLICATED)

        if task.parent_message_id:
            parent_message = self.fetch_message(task.parent_message_id)

            # check tree state
            if check_tree_state:
                # We store messages even after a tree has been completed.
                # Although these messages will never be labeled nor ranked they should be
                # included in the dataset because sometime users put a lot of effort into
                # writing their reply.

                ts = self.fetch_tree_state(parent_message.message_tree_id)
                if ts.state not in (
                    message_tree_state.State.GROWING,
                    message_tree_state.State.RANKING,
                    message_tree_state.State.READY_FOR_SCORING,
                    message_tree_state.State.READY_FOR_EXPORT,
                ):
                    raise OasstError(
                        "Message insertion failed. Message tree is no longer accepting messages.",
                        OasstErrorCode.TREE_IN_ABORTED_STATE,
                    )
                if not ts.active:
                    logger.warning(
                        f"Received messsage for inactive tree {parent_message.message_tree_id} (state='{ts.state.value}')."
                    )

            if check_duplicate and not settings.DEBUG_ALLOW_DUPLICATE_TASKS:
                siblings = self.fetch_message_children(task.parent_message_id, review_result=None, deleted=False)
                if any(m.user_id == self.user_id for m in siblings):
                    raise OasstError(
                        "User cannot reply twice to the same message.",
                        OasstErrorCode.TASK_MESSAGE_DUPLICATE_REPLY,
                    )

            parent_message.message_tree_id
            parent_message.children_count += 1
            self.db.add(parent_message)

            depth = parent_message.depth + 1
            deleted = parent_message.deleted

        task_payload: db_payload.TaskPayload = task.payload.payload
        if isinstance(task_payload, db_payload.InitialPromptPayload):
            role = "prompter"
        elif isinstance(task_payload, db_payload.PrompterReplyPayload):
            role = "prompter"
        elif isinstance(task_payload, db_payload.AssistantReplyPayload):
            role = "assistant"
        elif isinstance(task_payload, db_payload.SummarizationStoryPayload):
            raise NotImplementedError("SummarizationStory task not implemented.")
        else:
            raise OasstError(
                f"Unexpected task payload type: {type(task_payload).__name__}",
                OasstErrorCode.TASK_UNEXPECTED_PAYLOAD_TYPE_,
            )

        assert role in ("assistant", "prompter")

        # create reply message
        new_message_id = uuid4()
        user_message = self.insert_message(
            message_id=new_message_id,
            frontend_message_id=user_frontend_message_id,
            parent_id=task.parent_message_id,
            message_tree_id=task.message_tree_id or new_message_id,
            task_id=task.id,
            role=role,
            payload=db_payload.MessagePayload(text=text),
            lang=lang or "en",
            depth=depth,
            review_count=review_count,
            review_result=review_result,
            deleted=deleted,
        )
        if not task.collective:
            task.done = True
            self.db.add(task)
        self.journal.log_text_reply(task=task, message_id=new_message_id, role=role, length=len(text))
        logger.debug(
            f"Inserted message id={user_message.id}, tree={user_message.message_tree_id}, user_id={user_message.user_id}, "
            f"text[:100]='{user_message.text[:100]}', role='{user_message.role}', lang='{user_message.lang}'"
        )
        return user_message

    @managed_tx_method(CommitMode.FLUSH)
    def store_rating(self, rating: protocol_schema.MessageRating) -> MessageReaction:
        message = self.fetch_message_by_frontend_message_id(rating.message_id, fail_if_missing=True)

        task = self.task_repository.fetch_task_by_frontend_message_id(rating.message_id)
        self._validate_task(task)
        task_payload: db_payload.RateSummaryPayload = task.payload.payload
        if type(task_payload) != db_payload.RateSummaryPayload:
            raise OasstError(
                f"Task payload type mismatch: {type(task_payload)=} != {db_payload.RateSummaryPayload}",
                OasstErrorCode.TASK_PAYLOAD_TYPE_MISMATCH,
            )

        if rating.rating < task_payload.scale.min or rating.rating > task_payload.scale.max:
            raise OasstError(
                f"Invalid rating value: {rating.rating=} not in {task_payload.scale=}",
                OasstErrorCode.RATING_OUT_OF_RANGE,
            )

        # store reaction to message
        reaction_payload = db_payload.RatingReactionPayload(rating=rating.rating)
        reaction = self.insert_reaction(task_id=task.id, payload=reaction_payload, message_id=message.id)
        if not task.collective:
            task.done = True
            self.db.add(task)

        self.journal.log_rating(task, message_id=message.id, rating=rating.rating)
        logger.info(f"Ranking {rating.rating} stored for task {task.id}.")
        return reaction

    @managed_tx_method(CommitMode.COMMIT)
    def store_ranking(self, ranking: protocol_schema.MessageRanking) -> tuple[MessageReaction, Task]:
        # fetch task
        task = self.task_repository.fetch_task_by_frontend_message_id(ranking.message_id)
        self._validate_task(task, frontend_message_id=ranking.message_id)
        if not task.collective:
            task.done = True
            self.db.add(task)

        task_payload: db_payload.RankConversationRepliesPayload | db_payload.RankInitialPromptsPayload = (
            task.payload.payload
        )

        match type(task_payload):
            case db_payload.RankPrompterRepliesPayload | db_payload.RankAssistantRepliesPayload:
                # validate ranking
                if sorted(ranking.ranking) != list(range(num_replies := len(task_payload.reply_messages))):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_replies=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                last_conv_message = task_payload.conversation.messages[-1]
                parent_msg = self.fetch_message(last_conv_message.id)

                # store reaction to message
                ranked_message_ids = [task_payload.reply_messages[i].id for i in ranking.ranking]
                for mid in ranked_message_ids:
                    message = self.fetch_message(mid)
                    if message.parent_id != parent_msg.id:
                        raise OasstError("Corrupt reply ranking result", OasstErrorCode.CORRUPT_RANKING_RESULT)
                    message.ranking_count += 1
                    self.db.add(message)

                reaction_payload = db_payload.RankingReactionPayload(
                    ranking=ranking.ranking,
                    ranked_message_ids=ranked_message_ids,
                    ranking_parent_id=task_payload.ranking_parent_id,
                    message_tree_id=task_payload.message_tree_id,
                )
                reaction = self.insert_reaction(task_id=task.id, payload=reaction_payload, message_id=parent_msg.id)
                self.journal.log_ranking(task, message_id=parent_msg.id, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for task {task.id}.")

            case db_payload.RankInitialPromptsPayload:
                # validate ranking
                if sorted(ranking.ranking) != list(range(num_prompts := len(task_payload.prompt_messages))):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_prompts=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                # store reaction to message
                ranked_message_ids = [task_payload.prompt_messages[i].id for i in ranking.ranking]
                reaction_payload = db_payload.RankingReactionPayload(
                    ranking=ranking.ranking, ranked_message_ids=ranked_message_ids
                )
                reaction = self.insert_reaction(task_id=task.id, payload=reaction_payload, message_id=None)
                # self.journal.log_ranking(task, message_id=None, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for task {task.id}.")

            case _:
                raise OasstError(
                    f"task payload type mismatch: {type(task_payload)=} != {db_payload.RankConversationRepliesPayload}",
                    OasstErrorCode.TASK_PAYLOAD_TYPE_MISMATCH,
                )

        return reaction, task

    @managed_tx_method(CommitMode.FLUSH)
    def insert_toxicity(self, message_id: UUID, model: str, score: float, label: str) -> MessageToxicity:
        """Save the toxicity score of a new message in the database.
        Args:
            message_id (UUID): the identifier of the message we want to save its toxicity score
            model (str): the model used for creating the toxicity score
            score (float): the toxicity score that we obtained from the model
            label (str): the final classification in toxicity of the model
        Raises:
            OasstError: if misses some of the before params
        Returns:
            MessageToxicity: the instance in the database of the score saved for that message
        """

        message_toxicity = MessageToxicity(message_id=message_id, model=model, score=score, label=label)
        self.db.add(message_toxicity)
        return message_toxicity

    @managed_tx_method(CommitMode.FLUSH)
    def insert_message_embedding(self, message_id: UUID, model: str, embedding: list[float]) -> MessageEmbedding:
        """Insert the embedding of a new message in the database.

        Args:
            message_id (UUID): the identifier of the message we want to save its embedding
            model (str): the model used for creating the embedding
            embedding (list[float]): the values obtained from the message & model

        Raises:
            OasstError: if misses some of the before params

        Returns:
            MessageEmbedding: the instance in the database of the embedding saved for that message
        """

        message_embedding = MessageEmbedding(message_id=message_id, model=model, embedding=embedding)
        self.db.add(message_embedding)
        return message_embedding

    @managed_tx_method(CommitMode.FLUSH)
    def insert_reaction(
        self, task_id: UUID, payload: db_payload.ReactionPayload, message_id: Optional[UUID]
    ) -> MessageReaction:
        self.ensure_user_is_enabled()

        container = PayloadContainer(payload=payload)
        reaction = MessageReaction(
            task_id=task_id,
            user_id=self.user_id,
            payload=container,
            api_client_id=self.api_client.id,
            payload_type=type(payload).__name__,
            message_id=message_id,
        )
        self.db.add(reaction)
        return reaction

    @managed_tx_method(CommitMode.FLUSH)
    def store_text_labels(self, text_labels: protocol_schema.TextLabels) -> tuple[TextLabels, Task, Message]:
        self.ensure_user_is_enabled()

        valid_labels: Optional[list[str]] = None
        mandatory_labels: Optional[list[str]] = None
        text_labels_id: Optional[UUID] = None
        message_id: Optional[UUID] = text_labels.message_id

        task: Task = None
        if text_labels.task_id:
            logger.debug(f"text_labels reply has task_id {text_labels.task_id}")
            task = self.task_repository.fetch_task_by_id(text_labels.task_id)
            self._validate_task(task, task_id=text_labels.task_id)

            task_payload: db_payload.TaskPayload = task.payload.payload
            if isinstance(task_payload, db_payload.LabelInitialPromptPayload):
                if message_id and task_payload.message_id != message_id:
                    raise OasstError("Task message id mismatch", OasstErrorCode.TEXT_LABELS_WRONG_MESSAGE_ID)
                message_id = task_payload.message_id
                valid_labels = task_payload.valid_labels
                mandatory_labels = task_payload.mandatory_labels
            elif isinstance(task_payload, db_payload.LabelConversationReplyPayload):
                if message_id and message_id != message_id:
                    raise OasstError("Task message id mismatch", OasstErrorCode.TEXT_LABELS_WRONG_MESSAGE_ID)
                message_id = task_payload.message_id
                valid_labels = task_payload.valid_labels
                mandatory_labels = task_payload.mandatory_labels
            else:
                raise OasstError(
                    "Unexpected text_labels task payload",
                    OasstErrorCode.TASK_PAYLOAD_TYPE_MISMATCH,
                )

            logger.debug(f"text_labels reply: {valid_labels=}, {mandatory_labels=}")

            if valid_labels:
                if not all([label in valid_labels for label in text_labels.labels.keys()]):
                    raise OasstError("Invalid text label specified", OasstErrorCode.TEXT_LABELS_INVALID_LABEL)

            if isinstance(mandatory_labels, list):
                mandatory_set = set(mandatory_labels)
                if not mandatory_set.issubset(text_labels.labels.keys()):
                    missing = ", ".join(mandatory_set - text_labels.labels.keys())
                    raise OasstError(
                        f"Mandatory text labels missing: {missing}", OasstErrorCode.TEXT_LABELS_MANDATORY_LABEL_MISSING
                    )

            text_labels_id = task.id  # associate with task by sharing the id

            if not task.collective:
                task.done = True
                self.db.add(task)

        logger.debug(f"inserting TextLabels for {message_id=}, {text_labels_id=}")
        model = TextLabels(
            id=text_labels_id,
            api_client_id=self.api_client.id,
            message_id=message_id,
            user_id=self.user_id,
            text=text_labels.text,
            labels=text_labels.labels,
            task_id=task.id if task else None,
        )

        message: Message = None
        if message_id:
            if not task:
                # free labeling case

                if text_labels.is_report is True:
                    message = self.handle_message_emoji(
                        message_id, protocol_schema.EmojiOp.add, protocol_schema.EmojiCode.red_flag
                    )

                # update existing record for repeated updates (same user no task associated)
                existing_text_label = self.fetch_non_task_text_labels(message_id, self.user_id)
                if existing_text_label is not None:
                    existing_text_label.labels = text_labels.labels
                    model = existing_text_label

            else:
                # task based labeling case

                message = self.fetch_message(message_id, fail_if_missing=True)
                if not settings.DEBUG_ALLOW_SELF_LABELING and message.user_id == self.user_id:
                    raise OasstError(
                        "Labeling own message is not allowed.", OasstErrorCode.TEXT_LABELS_NO_SELF_LABELING
                    )

                existing_labels = self.fetch_message_text_labels(message_id, self.user_id)
                if not settings.DEBUG_ALLOW_DUPLICATE_TASKS and any(l.task_id for l in existing_labels):
                    raise OasstError(
                        "Message was already labeled by same user before.",
                        OasstErrorCode.TEXT_LABELS_DUPLICATE_TASK_REPLY,
                    )

                message.review_count += 1
                self.db.add(message)

        self.db.add(model)
        return model, task, message

    def fetch_random_message_tree(
        self,
        require_role: str = None,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        """
        Loads all messages of a random message_tree.

        :param require_role: If set loads only message_tree which has
            at least one message with given role.
        """
        distinct_message_trees = self.db.query(Message.message_tree_id).distinct(Message.message_tree_id)
        if require_role:
            distinct_message_trees = distinct_message_trees.filter(Message.role == require_role)
        if review_result is not None:
            distinct_message_trees = distinct_message_trees.filter(Message.review_result == review_result)
        distinct_message_trees = distinct_message_trees.subquery()

        random_message_tree_id = self.db.query(distinct_message_trees).order_by(func.random()).limit(1).scalar()
        if random_message_tree_id:
            return self.fetch_message_tree(random_message_tree_id, review_result=review_result, deleted=deleted)
        return None

    def fetch_random_conversation(
        self,
        last_message_role: str = None,
        message_tree_id: Optional[UUID] = None,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        """
        Picks a random linear conversation starting from any root message
        and ending somewhere in the message_tree, possibly at the root itself.

        :param last_message_role: If set will form a conversation ending with a message
            created by this role. Necessary for the tasks like "user_reply" where
            the user should reply as a human and hence the last message of the conversation
            needs to have "assistant" role.
        """
        if message_tree_id:
            messages_tree = self.fetch_message_tree(message_tree_id, review_result=review_result, deleted=deleted)
        else:
            messages_tree = self.fetch_random_message_tree(
                last_message_role, review_result=review_result, deleted=deleted
            )
        if not messages_tree:
            raise OasstError("No message tree found", OasstErrorCode.NO_MESSAGE_TREE_FOUND)

        if last_message_role:
            conv_messages = [m for m in messages_tree if m.role == last_message_role]
            conv_messages = [random.choice(conv_messages)]
        else:
            conv_messages = [random.choice(messages_tree)]
        messages_tree = {m.id: m for m in messages_tree}

        while True:
            if not conv_messages[-1].parent_id:
                # reached the start of the conversation
                break

            parent_message = messages_tree[conv_messages[-1].parent_id]
            conv_messages.append(parent_message)

        return list(reversed(conv_messages))

    def fetch_random_initial_prompts(self, size: int = 5):
        messages = self.db.query(Message).filter(Message.parent_id.is_(None)).order_by(func.random()).limit(size).all()
        return messages

    def fetch_message_tree(
        self,
        message_tree_id: UUID,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        qry = self.db.query(Message).filter(Message.message_tree_id == message_tree_id)
        if review_result is not None:
            qry = qry.filter(Message.review_result == review_result)
        if deleted is not None:
            qry = qry.filter(Message.deleted == deleted)
        return self._add_user_emojis_all(qry)

    def check_users_recent_replies_for_duplicates(self, text: str) -> bool:
        """
        Checks if the user has recently replied with the same text within a given time period.
        """

        user_id = self.user_id
        logger.debug(f"Checking for duplicate tasks for user {user_id}")
        # messages in the past 24 hours
        messages = (
            self.db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_date.desc())
            .filter(
                Message.created_date > utcnow() - timedelta(minutes=settings.DUPLICATE_MESSAGE_FILTER_WINDOW_MINUTES)
            )
            .all()
        )
        if not messages:
            return False
        for msg in messages:
            if msg.text == text:
                return True
        return False

    def fetch_user_message_trees(
        self, user_id: Message.user_id, reviewed: bool = True, include_deleted: bool = False
    ) -> list[Message]:
        qry = self.db.query(Message).filter(Message.user_id == user_id)
        if reviewed:
            qry = qry.filter(Message.review_result)
        if not include_deleted:
            qry = qry.filter(not_(Message.deleted))
        return self._add_user_emojis_all(qry)

    def fetch_multiple_random_replies(self, max_size: int = 5, message_role: str = None):
        """
        Fetch a conversation with multiple possible replies to it.

        This function finds a random message with >1 replies,
        forms a conversation from the corresponding message tree root up to this message
        and fetches up to max_size possible replies in continuation to this conversation.
        """
        parent = self.db.query(Message.id).filter(Message.children_count > 1)
        if message_role:
            parent = parent.filter(Message.role == message_role)

        parent = parent.order_by(func.random()).limit(1)
        replies = (
            self.db.query(Message).filter(Message.parent_id.in_(parent)).order_by(func.random()).limit(max_size).all()
        )
        if not replies:
            raise OasstError("No replies found", OasstErrorCode.NO_REPLIES_FOUND)

        message_tree = self.fetch_message_tree(replies[0].message_tree_id)
        message_tree = {p.id: p for p in message_tree}
        conversation = [message_tree[replies[0].parent_id]]
        while True:
            if not conversation[-1].parent_id:
                # reached start of the conversation
                break

            parent_message = message_tree[conversation[-1].parent_id]
            conversation.append(parent_message)

        conversation = reversed(conversation)

        return conversation, replies

    def fetch_message(self, message_id: UUID, fail_if_missing: bool = True) -> Optional[Message]:
        qry = self.db.query(Message).filter(Message.id == message_id)
        messages = self._add_user_emojis_all(qry)
        message = messages[0] if messages else None

        message = self.db.query(Message).filter(Message.id == message_id).one_or_none()
        if fail_if_missing and not message:
            raise OasstError("Message not found", OasstErrorCode.MESSAGE_NOT_FOUND, HTTPStatus.NOT_FOUND)
        return message

    def fetch_non_task_text_labels(self, message_id: UUID, user_id: UUID) -> Optional[TextLabels]:
        query = (
            self.db.query(TextLabels)
            .outerjoin(Task, Task.id == TextLabels.id)
            .filter(Task.id.is_(None), TextLabels.message_id == message_id, TextLabels.user_id == user_id)
        )
        text_label = query.one_or_none()
        return text_label

    def fetch_message_text_labels(self, message_id: UUID, user_id: Optional[UUID] = None) -> list[TextLabels]:
        query = self.db.query(TextLabels).filter(TextLabels.message_id == message_id)
        if user_id is not None:
            query = query.filter(TextLabels.user_id == user_id)
        return query.all()

    @staticmethod
    def trace_conversation(messages: list[Message] | dict[UUID, Message], last_message: Message) -> list[Message]:
        """
        Pick messages from a collection so that the result makes a linear conversation
        starting from a message tree root and up to the given message.
        Returns an ordered list of messages starting from the message tree root.
        """
        if isinstance(messages, list):
            messages = {m.id: m for m in messages}
        if not isinstance(messages, dict):
            # This should not normally happen
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR0, HTTPStatus.INTERNAL_SERVER_ERROR)

        conv = [last_message]
        while conv[-1].parent_id:
            if conv[-1].parent_id not in messages:
                # Can't form a continuous conversation
                raise OasstError(
                    "Broken conversation", OasstErrorCode.BROKEN_CONVERSATION, HTTPStatus.INTERNAL_SERVER_ERROR
                )

            parent_message = messages[conv[-1].parent_id]
            conv.append(parent_message)

        return list(reversed(conv))

    def fetch_message_conversation(self, message: Message | UUID) -> list[Message]:
        """
        Fetch a conversation from the tree root and up to this message.
        """
        if isinstance(message, UUID):
            message = self.fetch_message(message)

        tree_messages = self.fetch_message_tree(message.message_tree_id)
        return self.trace_conversation(tree_messages, message)

    def fetch_tree_from_message(
        self,
        message: Message | UUID,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        """
        Fetch message tree this message belongs to.
        """
        if isinstance(message, UUID):
            message = self.fetch_message(message)
        logger.debug(f"fetch_message_tree({message.message_tree_id=})")
        return self.fetch_message_tree(message.message_tree_id, review_result=review_result, deleted=deleted)

    def fetch_message_children(
        self,
        message: Message | UUID,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        """
        Get all direct children of this message
        """
        if isinstance(message, Message):
            message = message.id

        qry = self.db.query(Message).filter(Message.parent_id == message)
        if review_result is not None:
            qry = qry.filter(Message.review_result == review_result)
        if deleted is not None:
            qry = qry.filter(Message.deleted == deleted)
        children = self._add_user_emojis_all(qry)
        return children

    def fetch_message_siblings(
        self,
        message: Message | UUID,
        review_result: Optional[bool] = True,
        deleted: Optional[bool] = False,
    ) -> list[Message]:
        """
        Get siblings of a message (other messages with the same parent_id)
        """
        qry = self.db.query(Message)
        if isinstance(message, Message):
            qry = qry.filter(Message.parent_id == message.parent_id)
        else:
            parent_qry = self.db.query(Message.parent_id).filter(Message.id == message).subquery()
            qry = qry.filter(Message.parent_id == parent_qry.c.parent_id)

        if review_result is not None:
            qry = qry.filter(Message.review_result == review_result)
        if deleted is not None:
            qry = qry.filter(Message.deleted == deleted)
        siblings = self._add_user_emojis_all(qry)
        return siblings

    @staticmethod
    def trace_descendants(root: Message, messages: list[Message]) -> list[Message]:
        children = defaultdict(list)
        for msg in messages:
            children[msg.parent_id].append(msg)

        def _traverse_subtree(m: Message):
            for child in children[m.id]:
                yield child
                yield from _traverse_subtree(child)

        return list(_traverse_subtree(root))

    def fetch_message_descendants(self, message: Message | UUID, max_depth: int = None) -> list[Message]:
        """
        Find all descendant messages to this message.

        This function creates a subtree of messages starting from given root message.
        """
        if isinstance(message, UUID):
            message = self.fetch_message(message)

        desc = self.db.query(Message).filter(
            Message.message_tree_id == message.message_tree_id, Message.depth > message.depth
        )
        if max_depth is not None:
            desc = desc.filter(Message.depth <= max_depth)

        desc = self._add_user_emojis_all(desc)

        return self.trace_descendants(message, desc)

    def fetch_longest_conversation(self, message: Message | UUID) -> list[Message]:
        tree = self.fetch_tree_from_message(message)
        max_message = max(tree, key=lambda m: m.depth)
        return self.trace_conversation(tree, max_message)

    def fetch_message_with_max_children(self, message: Message | UUID) -> tuple[Message, list[Message]]:
        tree = self.fetch_tree_from_message(message)
        max_message = max(tree, key=lambda m: m.children_count)
        return max_message, [m for m in tree if m.parent_id == max_message.id]

    def _add_user_emojis_all(self, qry: Query) -> list[Message]:
        if self.user_id is None:
            return qry.all()

        order_by_clauses = qry._order_by_clauses
        sq = qry.subquery("m")
        qry = (
            self.db.query(Message, func.string_agg(MessageEmoji.emoji, literal_column("','")).label("user_emojis"))
            .select_entity_from(sq)
            .outerjoin(
                MessageEmoji,
                and_(
                    sq.c.id == MessageEmoji.message_id,
                    MessageEmoji.user_id == self.user_id,
                    sq.c.emojis != JSON.NULL,
                ),
            )
            .group_by(sq)
        )
        qry._order_by_clauses = order_by_clauses
        messages: list[Message] = []
        for x in qry:
            m: Message = x.Message
            user_emojis = x["user_emojis"]
            if user_emojis:
                m._user_emojis = user_emojis.split(",")
            m._user_is_author = self.user_id and self.user_id == m.user_id
            messages.append(m)
        return messages

    def query_messages_ordered_by_created_date(
        self,
        user_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
        username: Optional[str] = None,
        api_client_id: Optional[UUID] = None,
        gte_created_date: Optional[datetime] = None,
        gt_id: Optional[UUID] = None,
        lte_created_date: Optional[datetime] = None,
        lt_id: Optional[UUID] = None,
        only_roots: bool = False,
        deleted: Optional[bool] = None,
        review_result: Optional[bool] = None,
        desc: bool = False,
        limit: Optional[int] = 100,
        lang: Optional[str] = None,
    ) -> list[Message]:
        if not self.api_client.trusted:
            if not api_client_id:
                # Let unprivileged api clients query their own messages without api_client_id being set
                api_client_id = self.api_client.id

            if api_client_id != self.api_client.id:
                # Unprivileged api client asks for foreign messages
                raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTPStatus.FORBIDDEN)

        qry = self.db.query(Message)
        if user_id:
            qry = qry.filter(Message.user_id == user_id)
        if username or auth_method:
            if not (username and auth_method):
                raise OasstError("Auth method or username missing.", OasstErrorCode.AUTH_AND_USERNAME_REQUIRED)
            qry = qry.join(User)
            qry = qry.filter(User.username == username, User.auth_method == auth_method)
        if api_client_id:
            qry = qry.filter(Message.api_client_id == api_client_id)

        gte_created_date = unaware_to_utc(gte_created_date)
        lte_created_date = unaware_to_utc(lte_created_date)

        if gte_created_date is not None:
            if gt_id:
                qry = qry.filter(
                    or_(
                        Message.created_date > gte_created_date,
                        and_(Message.created_date == gte_created_date, Message.id > gt_id),
                    )
                )
            else:
                qry = qry.filter(Message.created_date >= gte_created_date)
        elif gt_id:
            raise OasstError("Need id and date for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if lte_created_date is not None:
            if lt_id:
                qry = qry.filter(
                    or_(
                        Message.created_date < lte_created_date,
                        and_(Message.created_date == lte_created_date, Message.id < lt_id),
                    )
                )
            else:
                qry = qry.filter(Message.created_date <= lte_created_date)
        elif lt_id:
            raise OasstError("Need id and date for keyset pagination", OasstErrorCode.GENERIC_ERROR)

        if only_roots:
            qry = qry.filter(Message.parent_id.is_(None))

        if deleted is not None:
            qry = qry.filter(Message.deleted == deleted)

        if review_result is not None:
            qry = qry.filter(Message.review_result == review_result)

        if lang is not None:
            qry = qry.filter(Message.lang == lang)

        if desc:
            qry = qry.order_by(Message.created_date.desc(), Message.id.desc())
        else:
            qry = qry.order_by(Message.created_date.asc(), Message.id.asc())

        if limit is not None:
            qry = qry.limit(limit)

        return self._add_user_emojis_all(qry)

    def update_children_counts(self, message_tree_id: UUID):
        sql_update_children_count = """
UPDATE message SET children_count = cc.children_count
FROM (
    SELECT m.id, count(c.id) - COALESCE(SUM(c.deleted::int), 0) AS children_count
    FROM message m
        LEFT JOIN message c ON m.id = c.parent_id
    WHERE m.message_tree_id  = :message_tree_id
    GROUP BY m.id
) AS cc
WHERE message.id = cc.id;
"""
        self.db.execute(text(sql_update_children_count), {"message_tree_id": message_tree_id})

    @managed_tx_method(CommitMode.COMMIT)
    def mark_messages_deleted(self, messages: Message | UUID | list[Message | UUID], recursive: bool = True):
        """
        Marks deleted messages and all their descendants.
        """
        if isinstance(messages, (Message, UUID)):
            messages = [messages]

        ids = []
        for message in messages:
            if isinstance(message, UUID):
                ids.append(message)
            elif isinstance(message, Message):
                ids.append(message.id)
            else:
                raise OasstError("Server error", OasstErrorCode.SERVER_ERROR1, HTTPStatus.INTERNAL_SERVER_ERROR)

        query = update(Message).where(Message.id.in_(ids)).values(deleted=True)
        self.db.execute(query)

        parent_ids = ids
        if recursive:
            while parent_ids:
                query = (
                    update(Message).filter(Message.parent_id.in_(parent_ids)).values(deleted=True).returning(Message.id)
                )

                parent_ids = self.db.execute(query).scalars().all()

    def get_stats(self) -> SystemStats:
        """
        Get data stats such as number of all messages in the system,
        number of deleted and active messages and number of message trees.
        """
        # With columns: lang, deleted, count
        group_count_query = self.db.query(Message.lang, Message.deleted, func.count()).group_by(
            Message.lang, Message.deleted
        )
        # With columns: None, None, count
        msg_tree_query = self.db.query(None, None, func.count(Message.id)).filter(Message.parent_id.is_(None))
        # Union both queries, so that we can fetch the counts in one database query
        query = group_count_query.union_all(msg_tree_query)

        nactives = 0
        ndeleted = 0
        nactives_by_lang = {}
        nthreads = 0

        for lang, deleted, count in query.all():
            if lang is None:  # corresponds to msg_tree_query
                nthreads = count
                continue
            if deleted is False:  # corresponds to group_count_query (lang, deleted=False)
                nactives_by_lang[lang] = count
                nactives += count
            else:  # corresponds to group_count_query (lang, deleted=True)
                ndeleted += count

        return SystemStats(
            all=nactives + ndeleted,
            active=nactives,
            active_by_lang=nactives_by_lang,
            deleted=ndeleted,
            message_trees=nthreads,
        )

    @managed_tx_method()
    def skip_task(self, task_id: UUID, reason: Optional[str]):
        self.ensure_user_is_enabled()

        task = self.task_repository.fetch_task_by_id(task_id)
        self._validate_task(task, check_ack=False)

        if not task.collective:
            task.skipped = True
            task.skip_reason = reason
            self.db.add(task)

        def handle_cancel_emoji(task_payload: db_payload.TaskPayload) -> Message | None:
            for types, emoji in _task_type_and_reaction:
                for t in types:
                    if isinstance(task_payload, t):
                        return self.handle_message_emoji(task.parent_message_id, protocol_schema.EmojiOp.add, emoji)
            return None

        task_payload: db_payload.TaskPayload = task.payload.payload
        handle_cancel_emoji(task_payload)

    def handle_message_emoji(
        self, message_id: UUID, op: protocol_schema.EmojiOp, emoji: protocol_schema.EmojiCode
    ) -> Message:
        self.ensure_user_is_enabled()

        message = self.fetch_message(message_id)

        # check if emoji exists
        existing_emoji = (
            self.db.query(MessageEmoji)
            .filter(
                MessageEmoji.message_id == message_id, MessageEmoji.user_id == self.user_id, MessageEmoji.emoji == emoji
            )
            .one_or_none()
        )

        if existing_emoji:
            if op == protocol_schema.EmojiOp.add:
                logger.info(f"Emoji record already exists {message_id=}, {emoji=}, {self.user_id=}")
                return message
            elif op == protocol_schema.EmojiOp.togggle:
                op = protocol_schema.EmojiOp.remove

        if existing_emoji is None:
            if op == protocol_schema.EmojiOp.remove:
                logger.info(f"Emoji record not found {message_id=}, {emoji=}, {self.user_id=}")
                return message
            elif op == protocol_schema.EmojiOp.togggle:
                op = protocol_schema.EmojiOp.add

        if op == protocol_schema.EmojiOp.add:
            # hard coded exclusivity of thumbs_up & thumbs_down
            if emoji == protocol_schema.EmojiCode.thumbs_up and message.has_user_emoji(
                protocol_schema.EmojiCode.thumbs_down.value
            ):
                message = self.handle_message_emoji(
                    message_id, protocol_schema.EmojiOp.remove, protocol_schema.EmojiCode.thumbs_down
                )
            elif emoji == protocol_schema.EmojiCode.thumbs_down and message.has_user_emoji(
                protocol_schema.EmojiCode.thumbs_up.value
            ):
                message = self.handle_message_emoji(
                    message_id, protocol_schema.EmojiOp.remove, protocol_schema.EmojiCode.thumbs_up
                )

            if message.user_id == self.user_id and emoji in (
                protocol_schema.EmojiCode.thumbs_up,
                protocol_schema.EmojiCode.thumbs_down,
            ):
                logger.debug(f"Ignoring add emoji op for user's own message ({emoji=})")
                return message

            # Add to flagged_message table if the red flag emoji is applied
            if emoji == protocol_schema.EmojiCode.red_flag:
                flagged_message = FlaggedMessage(message_id=message_id, processed=False, created_date=utcnow())
                insert_stmt = pg.insert(FlaggedMessage).values(**flagged_message.dict())
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    constraint="flagged_message_pkey", set_=flagged_message.dict()
                )
                self.db.execute(upsert_stmt)

            # insert emoji record & increment count
            message_emoji = MessageEmoji(message_id=message.id, user_id=self.user_id, emoji=emoji)
            self.db.add(message_emoji)
            emoji_counts = message.emojis
            if not emoji_counts:
                message.emojis = {emoji.value: 1}
            else:
                count = emoji_counts.get(emoji.value) or 0
                emoji_counts[emoji.value] = count + 1
            if message._user_emojis is None:
                message._user_emojis = []
            if emoji.value not in message._user_emojis:
                message._user_emojis.append(emoji.value)
        elif op == protocol_schema.EmojiOp.remove:
            # remove emoji record and & decrement count
            message = self.fetch_message(message_id)
            if message._user_emojis and emoji.value in message._user_emojis:
                message._user_emojis.remove(emoji.value)
            self.db.delete(existing_emoji)
            emoji_counts = message.emojis
            count = emoji_counts.get(emoji.value)
            if count is not None:
                if count == 1:
                    del emoji_counts[emoji.value]
                else:
                    emoji_counts[emoji.value] = count - 1
                flag_modified(message, "emojis")
                self.db.add(message)
        else:
            raise OasstError("Emoji op not supported", OasstErrorCode.EMOJI_OP_UNSUPPORTED)

        flag_modified(message, "emojis")
        self.db.add(message)
        self.db.flush()
        return message

    def fetch_flagged_messages(self, max_count: Optional[int]) -> list[FlaggedMessage]:
        qry = self.db.query(FlaggedMessage)
        if max_count is not None:
            qry = qry.limit(max_count)

        return qry.all()

    def process_flagged_message(self, message_id: UUID) -> FlaggedMessage:
        message = self.db.query(FlaggedMessage).get(message_id)

        if not message:
            raise OasstError("Message not found", OasstErrorCode.MESSAGE_NOT_FOUND, HTTPStatus.NOT_FOUND)

        message.processed = True
        self.db.commit()
        self.db.refresh(message)

        return message
