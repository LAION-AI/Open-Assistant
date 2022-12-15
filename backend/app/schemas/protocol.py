# -*- coding: utf-8 -*-
import enum
from typing import Literal, Optional, Union
from uuid import UUID, uuid4

import pydantic
from pydantic import BaseModel


class TaskRequestType(str, enum.Enum):
    generic = "generic"
    summarize_story = "summarize_story"
    rate_summary = "rate_summary"


class TaskRequest(BaseModel):
    """The frontend asks the backend for a task."""

    type: TaskRequestType = TaskRequestType.generic
    user_id: Optional[str] = None


class Task(BaseModel):
    """A task is a unit of work that the backend gives to the frontend."""

    id: UUID = pydantic.Field(default_factory=uuid4)
    type: str
    addressed_users: Optional[list[str]] = None


class TaskResponse(BaseModel):
    """A task response is a message from the frontend to acknowledge the given task."""

    type: str
    status: Literal["success", "failure"] = "success"


class PostCreatedTaskResponse(TaskResponse):
    type: Literal["post_created"] = "post_created"
    post_id: str


class RatingCreatedTaskResponse(TaskResponse):
    type: Literal["rating_created"] = "rating_created"
    post_id: str


AnyTaskResponse = Union[
    PostCreatedTaskResponse,
    RatingCreatedTaskResponse,
]


class SummarizeStoryTask(Task):
    type: Literal["summarize_story"] = "summarize_story"
    story: str


class RatingScale(BaseModel):
    min: int
    max: int


class RateSummaryTask(Task):
    type: Literal["rate_summary"] = "rate_summary"
    full_text: str
    summary: str
    scale: RatingScale = RatingScale(min=1, max=5)


class TaskDone(Task):
    type: Literal["task_done"] = "task_done"
    reply_to_post_id: str


AnyTask = Union[
    SummarizeStoryTask,
    RateSummaryTask,
    TaskDone,
]


class Interaction(BaseModel):
    """An interaction is a message from the frontend to the backend."""

    type: str
    user_id: str


class TextReplyToPost(Interaction):
    """A user has replied to a post with text."""

    type: Literal["text_reply_to_post"] = "text_reply_to_post"
    post_id: str
    user_post_id: str
    text: str


class PostRating(Interaction):
    """A user has replied to a post with text."""

    type: Literal["post_rating"] = "post_rating"
    post_id: str
    rating: int


AnyInteraction = Union[
    TextReplyToPost,
    PostRating,
]
