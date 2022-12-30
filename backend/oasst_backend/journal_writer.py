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
    text_reply_to_message = "text_reply_to_message"
    message_rating = "message_rating"
    message_ranking = "message_ranking"


@payload_type
class JournalEvent(BaseModel):
    type: str
    user_id: Optional[UUID]
    message_id: Optional[UUID]
    workpackage_id: Optional[UUID]
    task_type: Optional[str]


@payload_type
class TextReplyEvent(JournalEvent):
    type: Literal[JournalEventType.text_reply_to_message] = JournalEventType.text_reply_to_message
    length: int
    role: str


@payload_type
class RatingEvent(JournalEvent):
    type: Literal[JournalEventType.message_rating] = JournalEventType.message_rating
    rating: int


@payload_type
class RankingEvent(JournalEvent):
    type: Literal[JournalEventType.message_ranking] = JournalEventType.message_ranking
    ranking: list[int]


class JournalWriter:
    def __init__(self, db: Session, api_client: ApiClient, user: User):
        self.db = db
        self.api_client = api_client
        self.user = user
        self.user_id = self.user.id if self.user else None

    def log_text_reply(self, work_package: WorkPackage, message_id: UUID, role: str, length: int) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.text_reply_to_message,
            payload=TextReplyEvent(role=role, length=length),
            workpackage_id=work_package.id,
            message_id=message_id,
        )

    def log_rating(self, work_package: WorkPackage, message_id: UUID, rating: int) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.message_rating,
            payload=RatingEvent(rating=rating),
            workpackage_id=work_package.id,
            message_id=message_id,
        )

    def log_ranking(self, work_package: WorkPackage, message_id: UUID, ranking: list[int]) -> Journal:
        return self.log(
            task_type=work_package.payload_type,
            event_type=JournalEventType.message_ranking,
            payload=RankingEvent(ranking=ranking),
            workpackage_id=work_package.id,
            message_id=message_id,
        )

    def log(
        self,
        *,
        payload: JournalEvent,
        task_type: str,
        event_type: str = None,
        workpackage_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None,
        commit: bool = True,
    ) -> Journal:
        if event_type is None:
            if payload is None:
                event_type = "null"
            else:
                event_type = type(payload).__name__

        if payload.user_id is None:
            payload.user_id = self.user_id
        if payload.message_id is None:
            payload.message_id = message_id
        if payload.workpackage_id is None:
            payload.workpackage_id = workpackage_id
        if payload.task_type is None:
            payload.task_type = task_type

        entry = Journal(
            user_id=self.user_id,
            api_client_id=self.api_client.id,
            created_date=utcnow(),
            event_type=event_type,
            event_payload=PayloadContainer(payload=payload),
            message_id=message_id,
        )

        self.db.add(entry)
        if commit:
            self.db.commit()

        return entry
