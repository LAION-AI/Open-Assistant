# -*- coding: utf-8 -*-
import random
from typing import Optional
from uuid import UUID, uuid4

import oasst_backend.models.db_payload as db_payload
from loguru import logger
from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.journal_writer import JournalWriter
from oasst_backend.models import ApiClient, User, Message, MessageReaction, TextLabels, WorkPackage
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session, func


class PromptRepository:
    def __init__(self, db: Session, api_client: ApiClient, user: Optional[protocol_schema.User]):
        self.db = db
        self.api_client = api_client
        self.user = self.lookup_user(user)
        self.user_id = self.user.id if self.user else None
        self.journal = JournalWriter(db, api_client, self.user)

    def lookup_user(self, user: protocol_schema.User) -> User:
        if not user:
            return None
        user: User = (
            self.db.query(User)
            .filter(
                User.api_client_id == self.api_client.id,
                User.username == user.id,
                User.auth_method == user.auth_method,
            )
            .first()
        )
        if user is None:
            # user is unknown, create new record
            user = User(
                username=user.id,
                display_name=user.display_name,
                api_client_id=self.api_client.id,
                auth_method=user.auth_method,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif user.display_name and user.display_name != user.display_name:
            # we found the user but the display name changed
            user.display_name = user.display_name
            self.db.add(user)
            self.db.commit()
        return user

    def validate_message_id(self, message_id: str) -> None:
        if not isinstance(message_id, str):
            raise OasstError(f"message_id must be string, not {type(message_id)}", OasstErrorCode.INVALID_POST_ID)
        if not message_id:
            raise OasstError("message_id must not be empty", OasstErrorCode.INVALID_POST_ID)

    def bind_frontend_message_id(self, task_id: UUID, message_id: str):
        self.validate_message_id(message_id)

        # find work package
        work_pack: WorkPackage = (
            self.db.query(WorkPackage)
            .filter(WorkPackage.id == task_id, WorkPackage.api_client_id == self.api_client.id)
            .first()
        )
        if work_pack is None:
            raise OasstError(f"WorkPackage for task {task_id} not found", OasstErrorCode.WORK_PACKAGE_NOT_FOUND)
        if work_pack.expired:
            raise OasstError("WorkPackage already expired.", OasstErrorCode.WORK_PACKAGE_EXPIRED)
        if work_pack.done or work_pack.ack is not None:
            raise OasstError("WorkPackage already updated.", OasstErrorCode.WORK_PACKAGE_ALREADY_UPDATED)

        work_pack.frontend_ref_message_id = message_id
        work_pack.ack = True
        # ToDo: check race-condition, transaction
        self.db.add(work_pack)
        self.db.commit()

    def acknowledge_task_failure(self, task_id):
        # find work package
        work_pack: WorkPackage = (
            self.db.query(WorkPackage)
            .filter(WorkPackage.id == task_id, WorkPackage.api_client_id == self.api_client.id)
            .first()
        )
        if work_pack is None:
            raise OasstError(f"WorkPackage for task {task_id} not found", OasstErrorCode.WORK_PACKAGE_NOT_FOUND)
        if work_pack.expired:
            raise OasstError("WorkPackage already expired.", OasstErrorCode.WORK_PACKAGE_EXPIRED)
        if work_pack.done or work_pack.ack is not None:
            raise OasstError("WorkPackage already updated.", OasstErrorCode.WORK_PACKAGE_ALREADY_UPDATED)

        work_pack.ack = False
        # ToDo: check race-condition, transaction
        self.db.add(work_pack)
        self.db.commit()

    def fetch_message_by_frontend_message_id(self, frontend_message_id: str, fail_if_missing: bool = True) -> Message:
        self.validate_message_id(frontend_message_id)
        message: Message = (
            self.db.query(Message)
            .filter(Message.api_client_id == self.api_client.id, Message.frontend_message_id == frontend_message_id)
            .one_or_none()
        )
        if fail_if_missing and message is None:
            raise OasstError(f"Message with message_id {frontend_message_id} not found.", OasstErrorCode.POST_NOT_FOUND)
        return message

    def fetch_workpackage_by_message_id(self, message_id: str) -> WorkPackage:
        self.validate_message_id(message_id)
        work_pack = (
            self.db.query(WorkPackage)
            .filter(WorkPackage.api_client_id == self.api_client.id, WorkPackage.frontend_ref_message_id == message_id)
            .one_or_none()
        )
        return work_pack

    def store_text_reply(self, text: str, message_id: str, user_message_id: str, role: str = None) -> Message:
        self.validate_message_id(message_id)
        self.validate_message_id(user_message_id)

        wp = self.fetch_workpackage_by_message_id(message_id)

        if wp is None:
            raise OasstError(f"WorkPackage for {message_id=} not found", OasstErrorCode.WORK_PACKAGE_NOT_FOUND)
        if wp.expired:
            raise OasstError("WorkPackage already expired.", OasstErrorCode.WORK_PACKAGE_EXPIRED)
        if not wp.ack:
            raise OasstError("WorkPackage is not acknowledged.", OasstErrorCode.WORK_PACKAGE_NOT_ACK)
        if wp.done:
            raise OasstError("WorkPackage already done.", OasstErrorCode.WORK_PACKAGE_ALREADY_DONE)

        # If there's no parent message assume user started new conversation
        role = "user"
        depth = 0

        if wp.parent_message_id:
            parent_message = self.fetch_message(wp.parent_message_id)
            parent_message.children_count += 1
            self.db.add(parent_message)

            depth = parent_message.depth + 1
            if parent_message.role == "assistant":
                role = "user"
            else:
                role = "assistant"

        # create reply message
        new_message_id = uuid4()
        user_message = self.insert_message(
            message_id=new_message_id,
            frontend_message_id=user_message_id,
            parent_id=wp.parent_message_id,
            thread_id=wp.thread_id or new_message_id,
            workpackage_id=wp.id,
            role=role,
            payload=db_payload.MessagePayload(text=text),
            depth=depth,
        )
        if not wp.collective:
            wp.done = True
            self.db.add(wp)
        self.db.commit()
        self.journal.log_text_reply(work_package=wp, message_id=new_message_id, role=role, length=len(text))
        return user_message

    def store_rating(self, rating: protocol_schema.MessageRating) -> MessageReaction:
        message = self.fetch_message_by_frontend_message_id(rating.message_id, fail_if_missing=True)

        work_package = self.fetch_workpackage_by_message_id(rating.message_id)
        work_payload: db_payload.RateSummaryPayload = work_package.payload.payload
        if type(work_payload) != db_payload.RateSummaryPayload:
            raise OasstError(
                f"work_package payload type mismatch: {type(work_payload)=} != {db_payload.RateSummaryPayload}",
                OasstErrorCode.WORK_PACKAGE_PAYLOAD_TYPE_MISMATCH,
            )

        if rating.rating < work_payload.scale.min or rating.rating > work_payload.scale.max:
            raise OasstError(
                f"Invalid rating value: {rating.rating=} not in {work_payload.scale=}",
                OasstErrorCode.RATING_OUT_OF_RANGE,
            )

        # store reaction to message
        reaction_payload = db_payload.RatingReactionPayload(rating=rating.rating)
        reaction = self.insert_reaction(message.id, reaction_payload)
        if not work_package.collective:
            work_package.done = True
            self.db.add(work_package)

        self.journal.log_rating(work_package, message_id=message.id, rating=rating.rating)
        logger.info(f"Ranking {rating.rating} stored for work_package {work_package.id}.")
        return reaction

    def store_ranking(self, ranking: protocol_schema.MessageRanking) -> MessageReaction:
        # fetch work_package
        work_package = self.fetch_workpackage_by_message_id(ranking.message_id)
        if not work_package.collective:
            work_package.done = True
            self.db.add(work_package)

        work_payload: db_payload.RankConversationRepliesPayload | db_payload.RankInitialPromptsPayload = (
            work_package.payload.payload
        )

        match type(work_payload):

            case db_payload.RankUserRepliesPayload | db_payload.RankAssistantRepliesPayload:
                # validate ranking
                num_replies = len(work_payload.replies)
                if sorted(ranking.ranking) != list(range(num_replies)):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_replies=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                # store reaction to message
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(work_package.id, reaction_payload)
                # TODO: resolve message_id
                self.journal.log_ranking(work_package, message_id=None, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for work_package {work_package.id}.")

                return reaction

            case db_payload.RankInitialPromptsPayload:
                # validate ranking
                if sorted(ranking.ranking) != list(range(num_prompts := len(work_payload.prompts))):
                    raise OasstError(
                        f"Invalid ranking submitted. Each reply index must appear exactly once ({num_prompts=}).",
                        OasstErrorCode.INVALID_RANKING_VALUE,
                    )

                # store reaction to message
                reaction_payload = db_payload.RankingReactionPayload(ranking=ranking.ranking)
                reaction = self.insert_reaction(work_package.id, reaction_payload)
                # TODO: resolve message_id
                self.journal.log_ranking(work_package, message_id=None, ranking=ranking.ranking)

                logger.info(f"Ranking {ranking.ranking} stored for work_package {work_package.id}.")

                return reaction

            case _:
                raise OasstError(
                    f"work_package payload type mismatch: {type(work_payload)=} != {db_payload.RankConversationRepliesPayload}",
                    OasstErrorCode.WORK_PACKAGE_PAYLOAD_TYPE_MISMATCH,
                )

    def store_task(
        self,
        task: protocol_schema.Task,
        thread_id: UUID = None,
        parent_message_id: UUID = None,
        collective: bool = False,
    ) -> WorkPackage:
        payload: db_payload.TaskPayload
        match type(task):
            case protocol_schema.SummarizeStoryTask:
                payload = db_payload.SummarizationStoryPayload(story=task.story)

            case protocol_schema.RateSummaryTask:
                payload = db_payload.RateSummaryPayload(
                    full_text=task.full_text, summary=task.summary, scale=task.scale
                )

            case protocol_schema.InitialPromptTask:
                payload = db_payload.InitialPromptPayload(hint=task.hint)

            case protocol_schema.UserReplyTask:
                payload = db_payload.UserReplyPayload(conversation=task.conversation, hint=task.hint)

            case protocol_schema.AssistantReplyTask:
                payload = db_payload.AssistantReplyPayload(type=task.type, conversation=task.conversation)

            case protocol_schema.RankInitialPromptsTask:
                payload = db_payload.RankInitialPromptsPayload(tpye=task.type, prompts=task.prompts)

            case protocol_schema.RankUserRepliesTask:
                payload = db_payload.RankUserRepliesPayload(
                    tpye=task.type, conversation=task.conversation, replies=task.replies
                )

            case protocol_schema.RankAssistantRepliesTask:
                payload = db_payload.RankAssistantRepliesPayload(
                    tpye=task.type, conversation=task.conversation, replies=task.replies
                )

            case _:
                raise OasstError(f"Invalid task type: {type(task)=}", OasstErrorCode.INVALID_TASK_TYPE)

        wp = self.insert_work_package(
            payload=payload, id=task.id, thread_id=thread_id, parent_message_id=parent_message_id, collective=collective
        )
        assert wp.id == task.id
        return wp

    def insert_work_package(
        self,
        payload: db_payload.TaskPayload,
        id: UUID = None,
        thread_id: UUID = None,
        parent_message_id: UUID = None,
        collective: bool = False,
    ) -> WorkPackage:
        c = PayloadContainer(payload=payload)
        wp = WorkPackage(
            id=id,
            user_id=self.user_id,
            payload_type=type(payload).__name__,
            payload=c,
            api_client_id=self.api_client.id,
            thread_id=thread_id,
            parent_message_id=parent_message_id,
            collective=collective,
        )
        self.db.add(wp)
        self.db.commit()
        self.db.refresh(wp)
        return wp

    def insert_message(
        self,
        *,
        message_id: UUID,
        frontend_message_id: str,
        parent_id: UUID,
        thread_id: UUID,
        workpackage_id: UUID,
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
            thread_id=thread_id,
            workpackage_id=workpackage_id,
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

    def insert_reaction(self, work_package_id: UUID, payload: db_payload.ReactionPayload) -> MessageReaction:
        if self.user_id is None:
            raise OasstError("User required", OasstErrorCode.USER_NOT_SPECIFIED)

        container = PayloadContainer(payload=payload)
        reaction = MessageReaction(
            work_package_id=work_package_id,
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
            text=text_labels.text,
            labels=text_labels.labels,
        )
        if text_labels.has_message_id:
            self.fetch_message_by_frontend_message_id(text_labels.message_id, fail_if_missing=True)
            model.message_id = text_labels.message_id
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def fetch_random_thread(self, require_role: str = None) -> list[Message]:
        """
        Loads all messages of a random thread.

        :param require_role: If set loads only thread which has
            at least one message with given role.
        """
        distinct_threads = self.db.query(Message.thread_id).distinct(Message.thread_id)
        if require_role:
            distinct_threads = distinct_threads.filter(Message.role == require_role)
        distinct_threads = distinct_threads.subquery()

        random_thread = self.db.query(distinct_threads).order_by(func.random()).limit(1)
        thread_messages = self.db.query(Message).filter(Message.thread_id.in_(random_thread)).all()
        return thread_messages

    def fetch_random_conversation(self, last_message_role: str = None) -> list[Message]:
        """
        Picks a random linear conversation starting from any root message
        and ending somewhere in the thread, possibly at the root itself.

        :param last_message_role: If set will form a conversation ending with a message
            created by this role. Necessary for the tasks like "user_reply" where
            the user should reply as a human and hence the last message of the conversation
            needs to have "assistant" role.
        """
        thread_messages = self.fetch_random_thread(last_message_role)
        if not thread_messages:
            raise OasstError("No threads found", OasstErrorCode.NO_THREADS_FOUND)
        if last_message_role:
            conv_messages = [p for p in thread_messages if p.role == last_message_role]
            conv_messages = [random.choice(conv_messages)]
        else:
            conv_messages = [random.choice(thread_messages)]
        thread_messages = {p.id: p for p in thread_messages}

        while True:
            if not conv_messages[-1].parent_id:
                # reached the start of the conversation
                break

            parent_message = thread_messages[conv_messages[-1].parent_id]
            conv_messages.append(parent_message)

        return list(reversed(conv_messages))

    def fetch_random_initial_prompts(self, size: int = 5):
        messages = self.db.query(Message).filter(Message.parent_id.is_(None)).order_by(func.random()).limit(size).all()
        return messages

    def fetch_thread(self, thread_id: UUID):
        return self.db.query(Message).filter(Message.thread_id == thread_id).all()

    def fetch_multiple_random_replies(self, max_size: int = 5, message_role: str = None):
        parent = self.db.query(Message.id).filter(Message.children_count > 1)
        if message_role:
            parent = parent.filter(Message.role == message_role)

        parent = parent.order_by(func.random()).limit(1)
        replies = self.db.query(Message).filter(Message.parent_id.in_(parent)).order_by(func.random()).limit(max_size).all()
        if not replies:
            raise OasstError("No replies found", OasstErrorCode.NO_REPLIES_FOUND)

        thread = self.fetch_thread(replies[0].thread_id)
        thread = {p.id: p for p in thread}
        thread_messages = [thread[replies[0].parent_id]]
        while True:
            if not thread_messages[-1].parent_id:
                # reached start of the conversation
                break

            parent_message = thread[thread_messages[-1].parent_id]
            thread_messages.append(parent_message)

        thread_messages = reversed(thread_messages)

        return thread_messages, replies

    def fetch_message(self, message_id: UUID) -> Optional[Message]:
        return self.db.query(Message).filter(Message.id == message_id).one()

    def close_task(self, message_id: str, allow_personal_tasks: bool = False):
        self.validate_message_id(message_id)
        wp = self.fetch_workpackage_by_message_id(message_id)

        if not wp:
            raise OasstError("Work package not found", OasstErrorCode.WORK_PACKAGE_NOT_FOUND)
        if wp.expired:
            raise OasstError("Work package expired", OasstErrorCode.WORK_PACKAGE_EXPIRED)
        if not allow_personal_tasks and not wp.collective:
            raise OasstError("This is not a collective task", OasstErrorCode.WORK_PACKAGE_NOT_COLLECTIVE)
        if wp.done:
            raise OasstError("Allready closed", OasstErrorCode.WORK_PACKAGE_ALREADY_DONE)

        wp.done = True
        self.db.add(wp)
        self.db.commit()
