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


class User(BaseModel):
    id: str
    name: str


class TaskRequest(BaseModel):
    """The frontend asks the backend for a task."""

    type: TaskRequestType = TaskRequestType.generic
    user: Optional[User] = None


class Task(BaseModel):
    """A task is a unit of work that the backend gives to the frontend."""

    id: UUID = pydantic.Field(default_factory=uuid4)
    type: str
    addressed_users: Optional[list[User]] = None


class TaskResponse(BaseModel):
    """A task response is a message from the frontend to acknowledge that an initial piece of work has been done on the task."""

    type: str
    status: Literal["success", "failure"] = "success"


class PostCreatedTaskResponse(TaskResponse):
    """The frontend signals to the backend that a post has been created."""

    type: Literal["post_created"] = "post_created"
    post_id: str


class RatingCreatedTaskResponse(TaskResponse):
    """The frontend signals to the backend that a rating input has been created for a given post."""

    type: Literal["rating_created"] = "rating_created"
    post_id: str


AnyTaskResponse = Union[
    PostCreatedTaskResponse,
    RatingCreatedTaskResponse,
]


class SummarizeStoryTask(Task):
    """A task to summarize a story."""

    type: Literal["summarize_story"] = "summarize_story"
    story: str


class RatingScale(BaseModel):
    min: int
    max: int


class RateSummaryTask(Task):
    """A task to rate a summary."""

    type: Literal["rate_summary"] = "rate_summary"
    full_text: str
    summary: str
    scale: RatingScale = RatingScale(min=1, max=5)


class TaskDone(Task):
    """Signals to the frontend that the task is done."""

    type: Literal["task_done"] = "task_done"
    reply_to_post_id: str


AnyTask = Union[
    SummarizeStoryTask,
    RateSummaryTask,
    TaskDone,
]


class Interaction(BaseModel):
    """An interaction is a user-generated action in the frontend."""

    type: str
    user: User


class TextReplyToPost(Interaction):
    """A user has replied to a post with text."""

    type: Literal["text_reply_to_post"] = "text_reply_to_post"
    post_id: str
    user_post_id: str
    text: str


class PostRating(Interaction):
    """A user has rated a post."""

    type: Literal["post_rating"] = "post_rating"
    post_id: str
    rating: int


AnyInteraction = Union[
    TextReplyToPost,
    PostRating,
]
