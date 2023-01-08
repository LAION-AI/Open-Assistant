from typing import Optional
from uuid import UUID

import oasst_backend.models.db_payload as db_payload
from oasst_backend.models import ApiClient, Task
from oasst_backend.models.payload_column_type import PayloadContainer
from oasst_backend.user_repository import UserRepository
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_404_NOT_FOUND


def validate_frontend_message_id(message_id: str) -> None:
    # TODO: Should it be replaced with fastapi/pydantic validation?
    if not isinstance(message_id, str):
        raise OasstError(
            f"message_id must be string, not {type(message_id)}", OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID
        )
    if not message_id:
        raise OasstError("message_id must not be empty", OasstErrorCode.INVALID_FRONTEND_MESSAGE_ID)


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
                payload = db_payload.RankInitialPromptsPayload(type=task.type, prompts=task.prompts)

            case protocol_schema.RankPrompterRepliesTask:
                payload = db_payload.RankPrompterRepliesPayload(
                    type=task.type, conversation=task.conversation, replies=task.replies
                )

            case protocol_schema.RankAssistantRepliesTask:
                payload = db_payload.RankAssistantRepliesPayload(
                    type=task.type, conversation=task.conversation, replies=task.replies
                )

            case protocol_schema.LabelInitialPromptTask:
                payload = db_payload.LabelInitialPromptPayload(
                    type=task.type, message_id=task.message_id, prompt=task.prompt, valid_labels=task.valid_labels
                )

            case protocol_schema.LabelPrompterReplyTask:
                payload = db_payload.LabelPrompterReplyPayload(
                    type=task.type,
                    message_id=task.message_id,
                    conversation=task.conversation,
                    reply=task.reply,
                    valid_labels=task.valid_labels,
                )

            case protocol_schema.LabelAssistantReplyTask:
                payload = db_payload.LabelAssistantReplyPayload(
                    type=task.type,
                    message_id=task.message_id,
                    conversation=task.conversation,
                    reply=task.reply,
                    valid_labels=task.valid_labels,
                )

            case _:
                raise OasstError(f"Invalid task type: {type(task)=}", OasstErrorCode.INVALID_TASK_TYPE)

        task = self.insert_task(
            payload=payload,
            id=task.id,
            message_tree_id=message_tree_id,
            parent_message_id=parent_message_id,
            collective=collective,
        )
        assert task.id == task.id
        return task

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
        # ToDo: check race-condition, transaction
        self.db.add(task)
        self.db.commit()

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
            raise OasstError("Allready closed", OasstErrorCode.TASK_ALREADY_DONE)

        task.done = True
        self.db.add(task)
        self.db.commit()

    def acknowledge_task_failure(self, task_id):
        # find task
        task: Task = self.db.query(Task).filter(Task.id == task_id, Task.api_client_id == self.api_client.id).first()
        if task is None:
            raise OasstError(f"Task for {task_id=} not found", OasstErrorCode.TASK_NOT_FOUND, HTTP_404_NOT_FOUND)
        if task.expired:
            raise OasstError("Task already expired.", OasstErrorCode.TASK_EXPIRED)
        if task.done or task.ack is not None:
            raise OasstError("Task already updated.", OasstErrorCode.TASK_ALREADY_UPDATED)

        task.ack = False
        # ToDo: check race-condition, transaction
        self.db.add(task)
        self.db.commit()

    def insert_task(
        self,
        payload: db_payload.TaskPayload,
        id: UUID = None,
        message_tree_id: UUID = None,
        parent_message_id: UUID = None,
        collective: bool = False,
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
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def fetch_task_by_frontend_message_id(self, message_id: str) -> Task:
        validate_frontend_message_id(message_id)
        task = (
            self.db.query(Task)
            .filter(Task.api_client_id == self.api_client.id, Task.frontend_message_id == message_id)
            .one_or_none()
        )
        return task
