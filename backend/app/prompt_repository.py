# -*- coding: utf-8 -*-
from typing import Literal, Optional
from uuid import UUID

# from app.models import ApiClient, Person, PersonStats, Post, PostReaction, WorkPackage
from app.models import ApiClient, Person, WorkPackage
from app.models.payload_column_type import PayloadContainer, payload_tpye
from app.schemas import protocol as protocol_schema
from pydantic import BaseModel
from sqlmodel import Session


@payload_tpye
class TaskPayload(BaseModel):
    type: str


@payload_tpye
class SummarizationStoryPayload(TaskPayload):
    type: Literal["summarize_story"] = "summarize_story"
    story: str


@payload_tpye
class RateSummaryPayload(TaskPayload):
    type: Literal["rate_summary"] = "rate_summary"
    full_text: str
    summary: str
    scale: protocol_schema.RatingScale


@payload_tpye
class InitialPromptPayload(TaskPayload):
    type: Literal["initial_prompt"] = "initial_prompt"
    hint: str


@payload_tpye
class UserReplyPayload(TaskPayload):
    type: Literal["user_reply"] = "user_reply"
    conversation: protocol_schema.Conversation
    hint: str | None


@payload_tpye
class AssistantReplyPayload(TaskPayload):
    type: Literal["assistant_reply"] = "assistant_reply"
    conversation: protocol_schema.Conversation


class PromptRepository:
    def __init__(self, db: Session, api_client: ApiClient, user: Optional[protocol_schema.User]):
        self.db = db
        self.api_client = api_client
        self.person = self.lookup_person(user)
        self.person_id = self.person.id if self.person else None

    def lookup_person(self, user: protocol_schema.User) -> Person:
        person: Person = (
            self.db.query(Person)
            .filter(Person.api_client_id == self.api_client.id and Person.username == user.id)
            .first()
        )
        if person is None:
            # user is unknown, create new record
            person = Person(username=user.id, display_name=user.display_name, api_client_id=self.api_client.id)
            self.db.add(person)
            self.db.commit()
            self.db.refresh(person)
        elif user.display_name and user.display_name != person.display_name:
            # we found the user but the display name changed
            person.display_name = user.display_name
            self.db.add(person)
            self.db.commit()
        return person

    def store_task(self, task: protocol_schema.Task) -> WorkPackage:
        payload: TaskPayload = None
        match type(task):
            case protocol_schema.SummarizeStoryTask:
                payload = SummarizationStoryPayload(story=task.story)

            case protocol_schema.RateSummaryTask:
                payload = RateSummaryPayload(full_text=task.full_text, summary=task.summary, scale=task.scale)

            case protocol_schema.InitialPromptTask:
                payload = InitialPromptPayload(hint=task.hint)

            case protocol_schema.UserReplyTask:
                payload = UserReplyPayload(conversation=task.conversation, hint=task.hint)

            case protocol_schema.AssistantReplyTask:
                payload = AssistantReplyPayload(type=task.type, conversation=task.conversation)

            case _:
                raise RuntimeError(
                    detail="Invalid task type.",
                )

        wp = self.insert_work_package(payload=payload, id=task.id)
        assert wp.id == task.id
        return wp

    def insert_work_package(self, payload: TaskPayload, id: UUID = None) -> WorkPackage:
        c = PayloadContainer(payload=payload)
        wp = WorkPackage(
            id=id,
            person_id=self.person_id,
            payload_type=type(payload).__name__,
            payload=c,
            api_client_id=self.api_client.id,
        )
        self.db.add(wp)
        self.db.commit()
        self.db.refresh(wp)
        return wp
