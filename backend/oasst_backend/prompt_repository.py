import datetime
import random
from collections import defaultdict
from http import HTTPStatus
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

import oasst_backend.models.db_payload as db_payload
import sqlalchemy as sa
from loguru import logger
from oasst_backend.journal_writer import JournalWriter
from oasst_backend.models import (
    ApiClient,
    Message,
    MessageEmbedding,
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
from sqlalchemy import update
from sqlmodel import Session, func
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


class PromptRepository:
    def __init__(
        self,
        db: Session,
        api_client: ApiClient,
        client_user: Optional[protocol_schema.User] = None,
        user_repository: Optional[UserRepository] = None,
        task_repository: Optional[TaskRepository] = None,
    ):
        self.db = db
        self.api_client = api_client
        self.user_repository = user_repository or UserRepository(db, api_client)
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
            raise OasstError("User account disabled", OasstErrorCode.USER_DISABLED)

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
                HTTP_404_NOT_FOUND,
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
        payload_type: str = None,
        depth: int = 0,
        review_count: int = 0,
        review_result: bool = False,
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
            depth=depth,
            review_count=review_count,
            review_result=review_result,
        )
        self.db.add(message)

        # self.db.refresh(message)
        return message

    def _validate_task(
        self, task: Task, *, task_id: Optional[UUID] = None, frontend_message_id: Optional[str] = None
    ) -> Task:
        if task is None:
            if task_id:
                raise OasstError(f"Task for {task_id=} not found", OasstErrorCode.TASK_NOT_FOUND)
            if frontend_message_id:
                raise OasstError(f"Task for {frontend_message_id=} not found", OasstErrorCode.TASK_NOT_FOUND)
            raise OasstError("Task not found", OasstErrorCode.TASK_NOT_FOUND)

        if task.expired:
            raise OasstError("Task already expired.", OasstErrorCode.TASK_EXPIRED)
        if not task.ack:
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
        frontend_message_id: str,
        user_frontend_message_id: str,
        review_count: int = 0,
        review_result: bool = False,
        check_tree_state: bool = True,
    ) -> Message:
        self.ensure_user_is_enabled()

        validate_frontend_message_id(frontend_message_id)
        validate_frontend_message_id(user_frontend_message_id)

        task = self.task_repository.fetch_task_by_frontend_message_id(frontend_message_id)
        self._validate_task(task)

        # If there's no parent message assume user started new conversation
        role = None
        depth = 0

        if task.parent_message_id:
            parent_message = self.fetch_message(task.parent_message_id)

            # check tree state
            if check_tree_state:
                ts = self.fetch_tree_state(parent_message.message_tree_id)
                if not ts.active or ts.state != message_tree_state.State.GROWING:
                    raise OasstError(
                        "Message insertion failed. Message tree is no longer in 'growing' state.",
                        OasstErrorCode.TREE_NOT_IN_GROWING_STATE,
                    )

            parent_message.message_tree_id
            parent_message.children_count += 1
            self.db.add(parent_message)

            depth = parent_message.depth + 1

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
            depth=depth,
            review_count=review_count,
            review_result=review_result,
        )
        if not task.collective:
            task.done = True
            self.db.add(task)
        self.journal.log_text_reply(task=task, message_id=new_message_id, role=role, length=len(text))
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
        reaction = self.insert_reaction(message.id, reaction_payload)
        if not task.collective:
            task.done = True
            self.db.add(task)

        self.journal.log_rating(task, message_id=message.id, rating=rating.rating)
        logger.info(f"Ranking {rating.rating} stored for task {task.id}.")
        return reaction

    @managed_tx_method(CommitMode.COMMIT)
    def store_ranking(self, ranking: protocol_schema.MessageRanking) -> Tuple[MessageReaction, Task]:
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
                reaction = self.insert_reaction(task.id, reaction_payload)
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
                reaction = self.insert_reaction(task.id, reaction_payload)
                # TODO: resolve message_id
                self.journal.log_ranking(task, message_id=None, ranking=ranking.ranking)

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
    def insert_message_embedding(self, message_id: UUID, model: str, embedding: List[float]) -> MessageEmbedding:
        """Insert the embedding of a new message in the database.

        Args:
            message_id (UUID): the identifier of the message we want to save its embedding
            model (str): the model used for creating the embedding
            embedding (List[float]): the values obtained from the message & model

        Raises:
            OasstError: if misses some of the before params

        Returns:
            MessageEmbedding: the instance in the database of the embedding saved for that message
        """

        message_embedding = MessageEmbedding(message_id=message_id, model=model, embedding=embedding)
        self.db.add(message_embedding)
        return message_embedding

    @managed_tx_method(CommitMode.FLUSH)
    def insert_reaction(self, task_id: UUID, payload: db_payload.ReactionPayload) -> MessageReaction:
        self.ensure_user_is_enabled()

        container = PayloadContainer(payload=payload)
        reaction = MessageReaction(
            task_id=task_id,
            user_id=self.user_id,
            payload=container,
            api_client_id=self.api_client.id,
            payload_type=type(payload).__name__,
        )
        self.db.add(reaction)
        return reaction

    @managed_tx_method(CommitMode.FLUSH)
    def store_text_labels(self, text_labels: protocol_schema.TextLabels) -> Tuple[TextLabels, Task, Message]:

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

            logger.debug(f"text_labels relpy: {valid_labels=}, {mandatory_labels=}")

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
        )

        if message_id:
            message = self.fetch_message(message_id)
            if task:
                message.review_count += 1
                self.db.add(message)

        self.db.add(model)
        return model, task, message

    def fetch_random_message_tree(self, require_role: str = None, reviewed: bool = True) -> list[Message]:
        """
        Loads all messages of a random message_tree.

        :param require_role: If set loads only message_tree which has
            at least one message with given role.
        """
        distinct_message_trees = self.db.query(Message.message_tree_id).distinct(Message.message_tree_id)
        if require_role:
            distinct_message_trees = distinct_message_trees.filter(Message.role == require_role)
        if reviewed:
            distinct_message_trees = distinct_message_trees.filter(Message.review_result)
        distinct_message_trees = distinct_message_trees.subquery()

        random_message_tree_id = self.db.query(distinct_message_trees).order_by(func.random()).limit(1).scalar()
        if random_message_tree_id:
            return self.fetch_message_tree(random_message_tree_id, reviewed)
        return None

    def fetch_random_conversation(
        self, last_message_role: str = None, message_tree_id: Optional[UUID] = None, reviewed: bool = True
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
            messages_tree = self.fetch_message_tree(message_tree_id, reviewed)
        else:
            messages_tree = self.fetch_random_message_tree(last_message_role)
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

    def fetch_message_tree(self, message_tree_id: UUID, reviewed: bool = True) -> list[Message]:
        qry = self.db.query(Message).filter(Message.message_tree_id == message_tree_id)
        if reviewed:
            qry = qry.filter(Message.review_result)
        return qry.all()

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
        message = self.db.query(Message).filter(Message.id == message_id).one_or_none()
        if fail_if_missing and not message:
            raise OasstError("Message not found", OasstErrorCode.MESSAGE_NOT_FOUND, HTTP_404_NOT_FOUND)
        return message

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

    def fetch_tree_from_message(self, message: Message | UUID) -> list[Message]:
        """
        Fetch message tree this message belongs to.
        """
        if isinstance(message, UUID):
            message = self.fetch_message(message)
        logger.debug(f"fetch_message_tree({message.message_tree_id=})")
        return self.fetch_message_tree(message.message_tree_id)

    def fetch_message_children(
        self, message: Message | UUID, reviewed: bool = True, exclude_deleted: bool = True
    ) -> list[Message]:
        """
        Get all direct children of this message
        """
        if isinstance(message, Message):
            message = message.id

        qry = self.db.query(Message).filter(Message.parent_id == message)
        if reviewed:
            qry = qry.filter(Message.review_result)
        if exclude_deleted:
            qry = qry.filter(Message.deleted == sa.false())
        children = qry.all()
        return children

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

        desc = desc.all()

        return self.trace_descendants(message, desc)

    def fetch_longest_conversation(self, message: Message | UUID) -> list[Message]:
        tree = self.fetch_tree_from_message(message)
        max_message = max(tree, key=lambda m: m.depth)
        return self.trace_conversation(tree, max_message)

    def fetch_message_with_max_children(self, message: Message | UUID) -> tuple[Message, list[Message]]:
        tree = self.fetch_tree_from_message(message)
        max_message = max(tree, key=lambda m: m.children_count)
        return max_message, [m for m in tree if m.parent_id == max_message.id]

    def query_messages(
        self,
        user_id: Optional[UUID] = None,
        auth_method: Optional[str] = None,
        username: Optional[str] = None,
        api_client_id: Optional[UUID] = None,
        desc: bool = True,
        limit: Optional[int] = 10,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        only_roots: bool = False,
        deleted: Optional[bool] = None,
    ) -> list[Message]:
        if not self.api_client.trusted and not api_client_id:
            # Let unprivileged api clients query their own messages without api_client_id being set
            api_client_id = self.api_client.id

        if not self.api_client.trusted and api_client_id != self.api_client.id:
            # Unprivileged api client asks for foreign messages
            raise OasstError("Forbidden", OasstErrorCode.API_CLIENT_NOT_AUTHORIZED, HTTP_403_FORBIDDEN)

        messages = self.db.query(Message)
        if user_id:
            messages = messages.filter(Message.user_id == user_id)
        if username or auth_method:
            if not username and auth_method:
                raise OasstError("Auth method or username missing.", OasstErrorCode.AUTH_AND_USERNAME_REQUIRED)
            messages = messages.join(User)
            messages = messages.filter(User.username == username, User.auth_method == auth_method)
        if api_client_id:
            messages = messages.filter(Message.api_client_id == api_client_id)

        if start_date:
            messages = messages.filter(Message.created_date >= start_date)
        if end_date:
            messages = messages.filter(Message.created_date < end_date)

        if only_roots:
            messages = messages.filter(Message.parent_id.is_(None))

        if deleted is not None:
            messages = messages.filter(Message.deleted == deleted)

        if desc:
            messages = messages.order_by(Message.created_date.desc())
        else:
            messages = messages.order_by(Message.created_date.asc())

        if limit is not None:
            messages = messages.limit(limit)

        return messages.all()

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
        deleted = self.db.query(Message.deleted, func.count()).group_by(Message.deleted)
        nthreads = self.db.query(None, func.count(Message.id)).filter(Message.parent_id.is_(None))
        query = deleted.union_all(nthreads)
        result = {k: v for k, v in query.all()}

        return SystemStats(
            all=result.get(True, 0) + result.get(False, 0),
            active=result.get(False, 0),
            deleted=result.get(True, 0),
            message_trees=result.get(None, 0),
        )
