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
    rank_initial_prompts = "rank_initial_prompts"
    rank_user_replies = "rank_user_replies"
    rank_assistant_replies = "rank_assistant_replies"


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
    collective: bool = False


class TaskAck(BaseModel):
    """The frontend acknowledges that it has received a task and created a post."""

    post_id: str


class TaskNAck(BaseModel):
    """The frontend acknowledges that it has received a task but cannot create a post."""

    reason: str


class TaskClose(BaseModel):
    """The frontend asks to mark task as done"""

    post_id: str


class Task(BaseModel):
    """A task is a unit of work that the backend gives to the frontend."""

    id: UUID = pydantic.Field(default_factory=uuid4)
    type: str


class SummarizeStoryTask(Task):
    """A task to summarize a story."""

    type: Literal["summarize_story"] = "summarize_story"
    story: str


class RatingScale(BaseModel):
    min: int
    max: int


class AbstractRatingTask(Task):
    """A task to rate something."""

    scale: RatingScale = RatingScale(min=1, max=5)


class RateSummaryTask(AbstractRatingTask):
    """A task to rate a summary."""

    type: Literal["rate_summary"] = "rate_summary"
    full_text: str
    summary: str


class WithHintMixin(BaseModel):
    hint: str | None = None  # provide a hint to the user to spark their imagination


class InitialPromptTask(Task, WithHintMixin):
    """A task to prompt the user to submit an initial prompt to the assistant."""

    type: Literal["initial_prompt"] = "initial_prompt"


class ReplyToConversationTask(Task):
    """A task to prompt the user to submit a reply to a conversation."""

    type: Literal["reply_to_conversation"] = "reply_to_conversation"
    conversation: Conversation  # the conversation so far


class UserReplyTask(ReplyToConversationTask, WithHintMixin):
    """A task to prompt the user to submit a reply to the assistant."""

    type: Literal["user_reply"] = "user_reply"


class AssistantReplyTask(ReplyToConversationTask):
    """A task to prompt the user to act as the assistant."""

    type: Literal["assistant_reply"] = "assistant_reply"


class RankInitialPromptsTask(Task):
    """A task to rank a set of initial prompts."""

    type: Literal["rank_initial_prompts"] = "rank_initial_prompts"
    prompts: list[str]


class RankConversationRepliesTask(Task):
    """A task to rank a set of replies to a conversation."""

    type: Literal["rank_conversation_replies"] = "rank_conversation_replies"
    conversation: Conversation  # the conversation so far
    replies: list[str]


class RankUserRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of user replies to a conversation."""

    type: Literal["rank_user_replies"] = "rank_user_replies"


class RankAssistantRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of assistant replies to a conversation."""

    type: Literal["rank_assistant_replies"] = "rank_assistant_replies"


class TaskDone(Task):
    """Signals to the frontend that the task is done."""

    type: Literal["task_done"] = "task_done"


AnyTask = Union[
    TaskDone,
    SummarizeStoryTask,
    RateSummaryTask,
    InitialPromptTask,
    ReplyToConversationTask,
    UserReplyTask,
    AssistantReplyTask,
    RankInitialPromptsTask,
    RankConversationRepliesTask,
    RankUserRepliesTask,
    RankAssistantRepliesTask,
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


class PostRanking(Interaction):
    """A user has given a ranking for a post."""

    type: Literal["post_ranking"] = "post_ranking"
    post_id: str
    ranking: list[int]


AnyInteraction = Union[
    TextReplyToPost,
    PostRating,
    PostRanking,
]


class TextLabel(str, enum.Enum):
    """A label for a piece of text."""

    spam = "spam"
    violence = "violence"
    sexual_content = "sexual_content"
    toxicity = "toxicity"
    political_content = "political_content"
    humor = "humor"
    sarcasm = "sarcasm"
    hate_speech = "hate_speech"
    profanity = "profanity"
    ad_hominem = "ad_hominem"
    insult = "insult"
    threat = "threat"
    aggressive = "aggressive"
    misleading = "misleading"
    helpful = "helpful"
    formal = "formal"
    cringe = "cringe"
    creative = "creative"
    beautiful = "beautiful"
    informative = "informative"
    based = "based"
    slang = "slang"


class TextLabels(BaseModel):
    """A set of labels for a piece of text."""

    text: str
    labels: dict[TextLabel, float]
    post_id: str | None = None

    @property
    def has_post_id(self) -> bool:
        """Whether this TextLabels has a post_id."""
        return bool(self.post_id)

    # check that each label value is between 0 and 1
    @pydantic.validator("labels")
    def check_label_values(cls, v):
        for key, value in v.items():
            if not (0 <= value <= 1):
                raise ValueError(f"Label values must be between 0 and 1, got {value} for {key}.")
        return v
