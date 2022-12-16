# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from app.models import ApiClient, Person, Post, WorkPackage
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

    def validate_post_id(self, post_id: str) -> None:
        if not isinstance(post_id, str):
            raise TypeError("post_id must be string")
        if not post_id:
            raise ValueError("post_id must not be empty")

    def bind_frontend_post_id(self, task_id: UUID, post_id: str):
        self.validate_post_id(post_id)

        # find work package
        work_pack: WorkPackage = (
            self.db.query(WorkPackage)
            .filter(WorkPackage.id == task_id and WorkPackage.api_client_id == self.api_client.id)
            .first()
        )
        if work_pack is None:
            raise RuntimeError(f"WorkPackage for task {task_id} not found")
        if work_pack.expiry_date is not None and datetime.utcnow() > work_pack.expiry_date:
            raise RuntimeError("WorkPackage already expired.")

        # ToDo: check race-condition, transaction

        # check if task thread exits
        thread_root = (
            self.db.query(Post)
            .filter(
                Post.workpackage_id == work_pack.id
                and Post.frontend_post_id == post_id
                and Post.parent_id is None
                and self.api_client == self.api_client
            )
            .one_or_none()
        )
        if thread_root is None:
            thread_id = uuid4()
            thread_root = Post(
                id=thread_id,
                thread_id=thread_id,
                role="system",
                person_id=work_pack.person_id,
                workpackage_id=work_pack.id,
                frontend_post_id=post_id,
                api_client_id=self.api_client.id,
                payload_type="bind",
            )
            self.db.add(thread_root)
            self.db.commit()
            self.db.refresh(thread_root)
        return thread_root

    def fetch_workpackage_by_postid(self, post_id: str) -> WorkPackage:
        self.validate_post_id(post_id)
        post: Post = (
            self.db.query(Post)
            .filter(Post.api_client_id == self.api_client.id and Post.frontend_post_id == post_id)
            .one_or_none()
        )
        if post is None:
            raise RuntimeError(f"Post with post_id {post_id} not found.")

        work_pack = self.db.query(WorkPackage).filter(WorkPackage.id == post.workpackage_id).one()
        return work_pack

    def store_text_reply(self, reply: protocol_schema.TextReplyToPost) -> Post:
        self.validate_post_id(reply.post_id)
        self.validate_post_id(reply.user_post_id)

        # find post with post-id
        parent_post: Post = (
            self.db.query(Post)
            .filter(
                Post.api_client_id == self.api_client.id
                and Post.frontend_post_id == reply.post_id
                and Post.person_id == self.person_id
            )
            .one_or_none()
        )
        if parent_post is None:
            raise RuntimeError(f"Post for post_id {reply.post_id} not found.")

        # create reply post
        user_post_id = uuid4()
        # ToDo: role user or agent?
        user_post = Post(
            id=user_post_id,
            parent_id=parent_post.id,
            thread_id=parent_post.thread_id,
            workpackage_id=parent_post.workpackage_id,
            person_id=self.person_id,
            role="unknown",
            frontend_post_id=reply.user_post_id,
            api_client_id=self.api_client.id,
        )
        self.db.add(user_post)
        self.db.commit()
        self.db.refresh(user_post)
        return user_post

    def store_rating(self, rating: protocol_schema.PostRating) -> Post:
        pass

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
