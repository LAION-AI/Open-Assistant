# -*- coding: utf-8 -*-
import enum
from typing import Literal, Optional, Union
from uuid import UUID, uuid4

import pydantic
from pydantic import BaseModel


class TaskRequestType(str, enum.Enum):
    random = "random"
    summarize_story = "summarize_story"
    rate_summary = "rate_summary"
    initial_prompt = "initial_prompt"
    user_reply = "user_reply"
    assistant_reply = "assistant_reply"


class User(BaseModel):
    id: str
    display_name: str
    auth_method: Literal["discord", "local"]


class ConversationMessage(BaseModel):
    """Represents a message in a conversation between the user and the assistant."""

    text: str
    is_assistant: bool


class Conversation(BaseModel):
    """Represents a conversation between the user and the assistant."""

    messages: list[ConversationMessage] = []


class TaskRequest(BaseModel):
    """The frontend asks the backend for a task."""

    type: TaskRequestType = TaskRequestType.random
    user: Optional[User] = None


class Task(BaseModel):
    """A task is a unit of work that the backend gives to the frontend."""

    id: UUID = pydantic.Field(default_factory=uuid4)
    type: str
    addressed_user: Optional[User] = None


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


class InitialPromptTask(Task):
    """A task to prompt the user to submit an initial prompt to the assistant."""

    type: Literal["initial_prompt"] = "initial_prompt"
    hint: str | None = (
        None  # provide a hint to the user to guide them a bit (i.e. "Ask the assistant to summarize something.")
    )


class UserReplyTask(Task):
    """A task to prompt the user to submit a reply to the assistant."""

    type: Literal["user_reply"] = "user_reply"
    conversation: Conversation  # the conversation so far
    hint: str | None = None  # e.g. "Try to ask for clarification."


class AssistantReplyTask(Task):
    """A task to prompt the user to act as the assistant."""

    type: Literal["assistant_reply"] = "assistant_reply"
    conversation: Conversation  # the conversation so far


class TaskDone(Task):
    """Signals to the frontend that the task is done."""

    type: Literal["task_done"] = "task_done"
    reply_to_post_id: str


AnyTask = Union[
    TaskDone,
    SummarizeStoryTask,
    RateSummaryTask,
    InitialPromptTask,
    UserReplyTask,
    AssistantReplyTask,
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
