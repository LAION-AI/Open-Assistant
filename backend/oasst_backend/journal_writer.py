# -*- coding: utf-8 -*-
import enum
from typing import Literal, Optional
from uuid import UUID

from oasst_backend.models import ApiClient, Journal, Person, WorkPackage
from oasst_backend.models.payload_column_type import PayloadContainer, payload_type
from oasst_shared.utils import utcnow
from pydantic import BaseModel
from sqlmodel import Session


class JournalEventType(str, enum.Enum):
    """A label for a piece of text."""

    user_created = "user_created"
    text_reply_to_post = "text_reply_to_post"
    post_rating = "post_rating"
    post_ranking = "post_ranking"


@payload_type
class JournalEvent(BaseModel):
    type: str
    person_id: Optional[UUID]
    post_id: Optional[UUID]
    workpackage_id: Optional[UUID]
    task_type: Optional[str]


@payload_type
class TextReplyEvent(JournalEvent):
    type: Literal[JournalEventType.text_reply_to_post] = JournalEventType.text_reply_to_post
    length: int
    role: str


@payload_type
class RatingEvent(JournalEvent):
    type: Literal[JournalEventType.post_rating] = JournalEventType.post_rating
    rating: int


@payload_type
class RankingEvent(JournalEvent):
    type: Literal[JournalEventType.post_ranking] = JournalEventType.post_ranking
    ranking: list[int]


class JournalWriter:
    def __init__(self, db: Session, api_client: ApiClient, person: Person):
        self.db = db
        self.api_client = api_client
        self.person = person
        self.person_id = self.person.id if self.person else None

    def log_text_reply(self, work_package: WorkPackage, post_id: UUID, role: str, length: int) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.text_reply_to_post,
            payload=TextReplyEvent(role=role, length=length),
            workpackage_id=work_package.id,
            post_id=post_id,
        )

    def log_rating(self, work_package: WorkPackage, post_id: UUID, rating: int) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.post_rating,
            payload=RatingEvent(rating=rating),
            workpackage_id=work_package.id,
            post_id=post_id,
        )

    def log_ranking(self, work_package: WorkPackage, post_id: UUID, ranking: list[int]) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.post_ranking,
            payload=RankingEvent(ranking=ranking),
            workpackage_id=work_package.id,
            post_id=post_id,
        )

    def log(
        self,
        *,
        payload: JournalEvent,
        task_type: str,
        event_type: str = None,
        workpackage_id: Optional[UUID] = None,
        post_id: Optional[UUID] = None,
        commit: bool = True,
    ) -> Journal:
        if event_type is None:
            if payload is None:
                event_type = "null"
            else:
                event_type = type(payload).__name__

        if payload.person_id is None:
            payload.person_id = self.person_id
        if payload.post_id is None:
            payload.post_id = post_id
        if payload.workpackage_id is None:
            payload.workpackage_id = workpackage_id
        if payload.task_type is None:
            payload.task_type = task_type

        entry = Journal(
            person_id=self.person_id,
            api_client_id=self.api_client.id,
            created_date=utcnow(),
            event_type=event_type,
            event_payload=PayloadContainer(payload=payload),
            post_id=post_id,
        )

        self.db.add(entry)
        if commit:
            self.db.commit()

        return entry
