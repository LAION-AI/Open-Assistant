import datetime
import random
from collections import defaultdict
from http import HTTPStatus
from typing import Optional
from uuid import UUID, uuid4

import oasst_backend.models.db_payload as db_payload
from loguru import logger
from oasst_backend.journal_writer import JournalWriter
from oasst_backend.models import ApiClient, Message, MessageReaction, TextLabels, User
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_backend.task_repository import TaskRepository, validate_frontend_message_id
from oasst_backend.user_repository import UserRepository
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
        self.task_repository = task_repository or TaskRepository(
            db, api_client, client_user, user_repository=self.user_repository
        )
        self.journal = JournalWriter(db, api_client, self.user)

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
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def store_text_reply(self, text: str, frontend_message_id: str, user_frontend_message_id: str) -> Message:
        validate_frontend_message_id(frontend_message_id)
        validate_frontend_message_id(user_frontend_message_id)

        task = self.task_repository.fetch_task_by_frontend_message_id(frontend_message_id)

        if task is None:
            raise OasstError(f"Task for {frontend_message_id=} not found", OasstErrorCode.TASK_NOT_FOUND)
        if task.expired:
            raise OasstError("Task already expired.", OasstErrorCode.TASK_EXPIRED)
        if not task.ack:
            raise OasstError("Task is not acknowledged.", OasstErrorCode.TASK_NOT_ACK)
        if task.done:
            raise OasstError("Task already done.", OasstErrorCode.TASK_ALREADY_DONE)

        # If there's no parent message assume user started new conversation
        role = "prompter"
        depth = 0

        if task.parent_message_id:
            parent_message = self.fetch_message(task.parent_message_id)
            parent_message.children_count += 1
            self.db.add(parent_message)

            depth = parent_message.depth + 1
            if parent_message.role == "assistant":
                role = "prompter"
            else:
                role = "assistant"

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
        )
        if not task.collective:
            task.done = True
            self.db.add(task)
        self.db.commit()
        self.journal.log_text_reply(task=task, message_id=new_message_id, role=role, length=len(text))
        return user_message

    def store_rating(self, rating: protocol_schema.MessageRating) -> MessageReaction:
        message = self.fetch_message_by_frontend_message_id(rating.message_id, fail_if_missing=True)

        task = self.task_repository.fetch_task_by_frontend_message_id(rating.message_id)
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

    def store_ranking(self, ranking: protocol_schema.MessageRanking) -> MessageReaction:
        # fetch task
        task = self.task_repository.fetch_task_by_frontend_message_id(ranking.message_id)
        if not task.collective:
            task.done = True
            self.db.add(task)

        task_payload: db_payload.RankConversationRepliesPayload | db_payload.RankInitialPromptsPayload = (
            task.payload.payload
        )

        match type(task_payload):

            case db_payload.RankPrompterRepliesPayload | db_payload.RankAssistantRepliesPayload:
                # validate ranking
                num_replies = len(task_payload.replies)
                if sorted(ranking.ranking) != list(range(num_replies)):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_replies=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                # store reaction to message
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(task.id, reaction_payload)
                # TODO: resolve message_id
                self.journal.log_ranking(task, message_id=None, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for task {task.id}.")

                return reaction

            case db_payload.RankInitialPromptsPayload:
                # validate ranking
                if sorted(ranking.ranking) != list(range(num_prompts := len(task_payload.prompts))):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_prompts=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                # store reaction to message
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(task.id, reaction_payload)
                # TODO: resolve message_id
                self.journal.log_ranking(task, message_id=None, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for task {task.id}.")

                return reaction

            case _:
                raise OasstError(
                    f"task payload type mismatch: {type(task_payload)=} != {db_payload.RankConversationRepliesPayload}",
                    OasstErrorCode.TASK_PAYLOAD_TYPE_MISMATCH,
                )

    def insert_reaction(self, task_id: UUID, payload: db_payload.ReactionPayload) -> MessageReaction:
        if self.user_id is None:
            raise OasstError("User required", OasstErrorCode.USER_NOT_SPECIFIED)

        container = PayloadContainer(payload=payload)
        reaction = MessageReaction(
            task_id=task_id,
            user_id=self.user_id,
            payload=container,
            api_client_id=self.api_client.id,
            payload_type=type(payload).__name__,
        )
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        return reaction

    def store_text_labels(self, text_labels: protocol_schema.TextLabels) -> TextLabels:
        model = TextLabels(
            api_client_id=self.api_client.id,
            message_id=text_labels.message_id,
            user_id=self.user_id,
            text=text_labels.text,
            labels=text_labels.labels,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def fetch_random_message_tree(self, require_role: str = None) -> list[Message]:
        """
        Loads all messages of a random message_tree.

        :param require_role: If set loads only message_tree which has
            at least one message with given role.
        """
        distinct_message_trees = self.db.query(Message.message_tree_id).distinct(Message.message_tree_id)
        if require_role:
            distinct_message_trees = distinct_message_trees.filter(Message.role == require_role)
        distinct_message_trees = distinct_message_trees.subquery()

        random_message_tree = self.db.query(distinct_message_trees).order_by(func.random()).limit(1)
        message_tree_messages = self.db.query(Message).filter(Message.message_tree_id.in_(random_message_tree)).all()
        return message_tree_messages

    def fetch_random_conversation(self, last_message_role: str = None) -> list[Message]:
        """
        Picks a random linear conversation starting from any root message
        and ending somewhere in the message_tree, possibly at the root itself.

        :param last_message_role: If set will form a conversation ending with a message
            created by this role. Necessary for the tasks like "user_reply" where
            the user should reply as a human and hence the last message of the conversation
            needs to have "assistant" role.
        """
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

    def fetch_message_tree(self, message_tree_id: UUID):
        return self.db.query(Message).filter(Message.message_tree_id == message_tree_id).all()

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
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

        conv = [last_message]
        while conv[-1].parent_id:
            if conv[-1].parent_id not in messages:
                # Can't form a continuous conversation
                raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

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
        return self.fetch_message_tree(message.message_tree_id)

    def fetch_message_children(self, message: Message | UUID) -> list[Message]:
        """
        Get all direct children of this message
        """
        if isinstance(message, Message):
            message = message.id

        children = self.db.query(Message).filter(Message.parent_id == message).all()
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
        if username:
            messages = messages.join(User)
            messages = messages.filter(User.username == username)
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

        # TODO: Pagination could be great at some point
        return messages.all()

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
                raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)

        query = update(Message).where(Message.id.in_(ids)).values(deleted=True)
        self.db.execute(query)

        parent_ids = ids
        if recursive:
            while parent_ids:
                query = (
                    update(Message).filter(Message.parent_id.in_(parent_ids)).values(deleted=True).returning(Message.id)
                )

                parent_ids = self.db.execute(query).scalars().all()

        self.db.commit()

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
