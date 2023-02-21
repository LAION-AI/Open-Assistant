from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import oasst_backend.models.db_payload as db_payload
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.models import ApiClient, Task
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_backend.user_repository import UserRepository
from oasst_backend.utils.database_utils import CommitMode, managed_tx_method
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.utils import utcnow
from sqlmodel import Session, delete, false, func, not_, or_
from starlette.status import HTTP_404_NOT_FOUND


def validate_frontend_message_id(message_id: str) -> None:
    # TODO: Should it be replaced with fastapi/pydantic validation?
    if not isinstance(message_id, str):
        raise OasstError(
            f"message_id must be string, not {type(message_id)}", OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID
        )
    if not message_id:
        raise OasstError("message_id must not be empty", OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID)


def delete_expired_tasks(session: Session) -> int:
    stm = delete(Task).where(Task.expiry_date < utcnow(), Task.done == false())
    result = session.exec(stm)
    logger.info(f"Deleted {result.rowcount} expired tasks.")
    return result.rowcount


class TaskRepository:
    def __init__(
        self,
        db: Session,
        api_client: ApiClient,
        client_user: Optional[protocol_schema.User],
        user_repository: UserRepository,
    ):
        self.db = db
        self.api_client = api_client
        self.user_repository = user_repository
        self.user = self.user_repository.lookup_client_user(client_user, create_missing=True)
        self.user_id = self.user.id if self.user else None

    def store_task(
        self,
        task: protocol_schema.Task,
        message_tree_id: UUID = None,
        parent_message_id: UUID = None,
        collective: bool = False,
    ) -> Task:
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

            case protocol_schema.PrompterReplyTask:
                payload = db_payload.PrompterReplyPayload(conversation=task.conversation, hint=task.hint)

            case protocol_schema.AssistantReplyTask:
                payload = db_payload.AssistantReplyPayload(type=task.type, conversation=task.conversation)

            case protocol_schema.RankInitialPromptsTask:
                payload = db_payload.RankInitialPromptsPayload(type=task.type, prompt_messages=task.prompt_messages)

            case protocol_schema.RankPrompterRepliesTask:
                payload = db_payload.RankPrompterRepliesPayload(
                    type=task.type,
                    conversation=task.conversation,
                    reply_messages=task.reply_messages,
                    ranking_parent_id=task.ranking_parent_id,
                    message_tree_id=task.message_tree_id,
                )

            case protocol_schema.RankAssistantRepliesTask:
                payload = db_payload.RankAssistantRepliesPayload(
                    type=task.type,
                    conversation=task.conversation,
                    reply_messages=task.reply_messages,
                    ranking_parent_id=task.ranking_parent_id,
                    message_tree_id=task.message_tree_id,
                )

            case protocol_schema.LabelInitialPromptTask:
                payload = db_payload.LabelInitialPromptPayload(
                    type=task.type,
                    message_id=task.message_id,
                    prompt=task.prompt,
                    valid_labels=task.valid_labels,
                    mandatory_labels=task.mandatory_labels,
                    mode=task.mode,
                )

            case protocol_schema.LabelPrompterReplyTask:
                payload = db_payload.LabelPrompterReplyPayload(
                    type=task.type,
                    message_id=task.message_id,
                    conversation=task.conversation,
                    valid_labels=task.valid_labels,
                    mandatory_labels=task.mandatory_labels,
                    mode=task.mode,
                )

            case protocol_schema.LabelAssistantReplyTask:
                payload = db_payload.LabelAssistantReplyPayload(
                    type=task.type,
                    message_id=task.message_id,
                    conversation=task.conversation,
                    valid_labels=task.valid_labels,
                    mandatory_labels=task.mandatory_labels,
                    mode=task.mode,
                )

            case _:
                raise OasstError(f"Invalid task type: {type(task)=}", OasstErrorCode.INVALID_TASK_TYPE)

        if not collective and settings.TASK_VALIDITY_MINUTES > 0:
            expiry_date = utcnow() + timedelta(minutes=settings.TASK_VALIDITY_MINUTES)
        else:
            expiry_date = None

        task_model = self.insert_task(
            payload=payload,
            id=task.id,
            message_tree_id=message_tree_id,
            parent_message_id=parent_message_id,
            collective=collective,
            expiry_date=expiry_date,
        )
        assert task_model.id == task.id
        return task_model

    @managed_tx_method(CommitMode.COMMIT)
    def bind_frontend_message_id(self, task_id: UUID, frontend_message_id: str):
        validate_frontend_message_id(frontend_message_id)

        # find task
        task: Task = self.db.query(Task).filter(Task.id == task_id, Task.api_client_id == self.api_client.id).first()
        if task is None:
            raise OasstError(f"Task for {task_id=} not found", OasstErrorCode.TASK_NOT_FOUND, HTTP_404_NOT_FOUND)
        if task.expired:
            raise OasstError("Task already expired.", OasstErrorCode.TASK_EXPIRED)
        if task.done or task.ack is not None:
            raise OasstError("Task already updated.", OasstErrorCode.TASK_ALREADY_UPDATED)

        task.frontend_message_id = frontend_message_id
        task.ack = True
        self.db.add(task)

    @managed_tx_method(CommitMode.COMMIT)
    def close_task(self, frontend_message_id: str, allow_personal_tasks: bool = False):
        """
        Mark task as done. No further messages will be accepted for this task.
        """
        validate_frontend_message_id(frontend_message_id)
        task = self.task_repository.fetch_task_by_frontend_message_id(frontend_message_id)

        if not task:
            raise OasstError(
                f"Task for {frontend_message_id=} not found", OasstErrorCode.TASK_NOT_FOUND, HTTP_404_NOT_FOUND
            )
        if task.expired:
            raise OasstError("Task already expired", OasstErrorCode.TASK_EXPIRED)
        if not allow_personal_tasks and not task.collective:
            raise OasstError("This is not a collective task", OasstErrorCode.TASK_NOT_COLLECTIVE)
        if task.done:
            raise OasstError("Already closed", OasstErrorCode.TASK_ALREADY_DONE)

        task.done = True
        self.db.add(task)

    @managed_tx_method(CommitMode.COMMIT)
    def insert_task(
        self,
        payload: db_payload.TaskPayload,
        id: UUID = None,
        message_tree_id: UUID = None,
        parent_message_id: UUID = None,
        collective: bool = False,
        expiry_date: datetime = None,
    ) -> Task:
        c = PayloadContainer(payload=payload)
        task = Task(
            id=id,
            user_id=self.user_id,
            payload_type=type(payload).__name__,
            payload=c,
            api_client_id=self.api_client.id,
            message_tree_id=message_tree_id,
            parent_message_id=parent_message_id,
            collective=collective,
            expiry_date=expiry_date,
        )
        logger.debug(f"inserting {task=}")
        self.db.add(task)
        return task

    def fetch_task_by_frontend_message_id(self, message_id: str) -> Task:
        validate_frontend_message_id(message_id)
        task = (
            self.db.query(Task)
            .filter(Task.api_client_id == self.api_client.id, Task.frontend_message_id == message_id)
            .one_or_none()
        )
        return task

    def fetch_task_by_id(self, task_id: UUID) -> Task:
        task = self.db.query(Task).filter(Task.api_client_id == self.api_client.id, Task.id == task_id).one_or_none()
        return task

    def fetch_recent_reply_tasks(
        self,
        max_age: timedelta = timedelta(minutes=5),
        done: bool = False,
        skipped: bool = False,
        limit: int = 100,
    ) -> list[Task]:
        qry = self.db.query(Task).filter(
            Task.created_date > func.current_timestamp() - max_age,
            or_(Task.payload_type == "AssistantReplyPayload", Task.payload_type == "PrompterReplyPayload"),
        )
        if done is not None:
            qry = qry.filter(Task.done == done)
        if skipped is not None:
            qry = qry.filter(Task.skipped == skipped)
        if limit:
            qry = qry.limit(limit)
        return qry.all()

    def delete_expired(self) -> int:
        return delete_expired_tasks(self.db)

    def fetch_pending_tasks_of_user(
        self,
        user_id: UUID,
        max_age: timedelta = timedelta(minutes=5),
        limit: int = 100,
    ) -> list[Task]:
        qry = (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.created_date > func.current_timestamp() - max_age,
                not_(Task.done),
                not_(Task.skipped),
            )
            .order_by(Task.created_date)
        )
        if limit:
            qry = qry.limit(limit)
        return qry.all()
