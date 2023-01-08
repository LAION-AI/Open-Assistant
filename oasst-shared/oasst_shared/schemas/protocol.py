import enum
from datetime import datetime
from typing import List, Literal, Optional, Union
from uuid import UUID, uuid4

import pydantic
from oasst_shared.exceptions import OasstErrorCode
from pydantic import BaseModel, Field, conint, conlist, constr


class TaskRequestType(str, enum.Enum):
    random = "random"
    summarize_story = "summarize_story"
    rate_summary = "rate_summary"
    initial_prompt = "initial_prompt"
    prompter_reply = "prompter_reply"
    assistant_reply = "assistant_reply"
    rank_initial_prompts = "rank_initial_prompts"
    rank_prompter_replies = "rank_prompter_replies"
    rank_assistant_replies = "rank_assistant_replies"
    label_initial_prompt = "label_initial_prompt"
    label_assistant_reply = "label_assistant_reply"
    label_prompter_reply = "label_prompter_reply"


class User(BaseModel):
    id: str
    display_name: str
    auth_method: Literal["discord", "local"]


class ConversationMessage(BaseModel):
    """Represents a message in a conversation between the user and the assistant."""

    text: str
    is_assistant: bool
    message_id: Optional[UUID] = None
    frontend_message_id: Optional[str] = None


class Conversation(BaseModel):
    """Represents a conversation between the prompter and the assistant."""

    messages: list[ConversationMessage] = []


class Message(ConversationMessage):
    id: UUID
    parent_id: Optional[UUID] = None
    created_date: Optional[datetime] = None


class MessageTree(BaseModel):
    """All messages belonging to the same message tree."""

    id: UUID
    messages: list[Message] = []


class TaskRequest(BaseModel):
    """The frontend asks the backend for a task."""

    type: TaskRequestType = TaskRequestType.random
    # Must use Field(..., nullable=True) to indicate to the OpenAPI schema that
    # this is optional. https://github.com/pydantic/pydantic/issues/1270
    user: Optional[User] = Field(None, nullable=True)
    collective: bool = False


class TaskAck(BaseModel):
    """The frontend acknowledges that it has received a task and created a message."""

    message_id: str


class TaskNAck(BaseModel):
    """The frontend acknowledges that it has received a task but cannot create a message."""

    reason: str


class TaskClose(BaseModel):
    """The frontend asks to mark task as done"""

    message_id: str


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


class PrompterReplyTask(ReplyToConversationTask, WithHintMixin):
    """A task to prompt the user to submit a reply to the assistant."""

    type: Literal["prompter_reply"] = "prompter_reply"


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


class RankPrompterRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of prompter replies to a conversation."""

    type: Literal["rank_prompter_replies"] = "rank_prompter_replies"


class RankAssistantRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of assistant replies to a conversation."""

    type: Literal["rank_assistant_replies"] = "rank_assistant_replies"


class LabelInitialPromptTask(Task):
    """A task to label an initial prompt."""

    type: Literal["label_initial_prompt"] = "label_initial_prompt"
    message_id: UUID
    prompt: str
    valid_labels: list[str]


class LabelConversationReplyTask(Task):
    """A task to label a reply to a conversation."""

    type: Literal["label_conversation_reply"] = "label_conversation_reply"
    conversation: Conversation  # the conversation so far
    message_id: UUID
    reply: str
    valid_labels: list[str]


class LabelPrompterReplyTask(LabelConversationReplyTask):
    """A task to label a prompter reply to a conversation."""

    type: Literal["label_prompter_reply"] = "label_prompter_reply"


class LabelAssistantReplyTask(LabelConversationReplyTask):
    """A task to label an assistant reply to a conversation."""

    type: Literal["label_assistant_reply"] = "label_assistant_reply"


class TaskDone(Task):
    """Signals to the frontend that the task is done."""

    type: Literal["task_done"] = "task_done"


AnyTask = Union[
    TaskDone,
    SummarizeStoryTask,
    RateSummaryTask,
    InitialPromptTask,
    ReplyToConversationTask,
    PrompterReplyTask,
    AssistantReplyTask,
    RankInitialPromptsTask,
    RankConversationRepliesTask,
    RankPrompterRepliesTask,
    RankAssistantRepliesTask,
    LabelInitialPromptTask,
    LabelConversationReplyTask,
    LabelPrompterReplyTask,
    LabelAssistantReplyTask,
]


class Interaction(BaseModel):
    """An interaction is a user-generated action in the frontend."""

    type: str
    user: User


class TextReplyToMessage(Interaction):
    """A user has replied to a message with text."""

    type: Literal["text_reply_to_message"] = "text_reply_to_message"
    message_id: str
    user_message_id: str
    text: constr(min_length=1, strip_whitespace=True)


class MessageRating(Interaction):
    """A user has rated a message."""

    type: Literal["message_rating"] = "message_rating"
    message_id: str
    rating: conint(gt=0)


class MessageRanking(Interaction):
    """A user has given a ranking for a message."""

    type: Literal["message_ranking"] = "message_ranking"
    message_id: str
    ranking: conlist(item_type=int, min_items=1)


class TextLabel(str, enum.Enum):
    """A label for a piece of text."""

    def __new__(cls, label: str, display_text: str = "", help_text: str = None):
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.display_text = display_text
        obj.help_text = help_text
        return obj

    spam = "spam", "Seems to be intentionally low-quality or irrelevant"
    fails_task = "fails_task", "Fails to follow the correct instruction / task"
    not_appropriate = "not_appropriate", "Inappropriate for customer assistant"
    violence = "violence", "Encourages or fails to discourage violence/abuse/terrorism/self-harm"
    excessive_harm = (
        "excessive_harm",
        "Content likely to cause excessive harm not justifiable in the context",
        "Harm refers to physical or mental damage or injury to someone or something. Excessive refers to a reasonable threshold of harm in the context, for instance damaging skin is not excessive in the context of surgery.",
    )
    sexual_content = "sexual_content", "Contains sexual content"
    toxicity = "toxicity", "Contains rude, abusive, profane or insulting content"
    moral_judgement = "moral_judgement", "Expresses moral judgement"
    political_content = "political_content", "Expresses political views"
    humor = "humor", "Contains humorous content including sarcasm"
    hate_speech = (
        "hate_speech",
        "Content is abusive or threatening and expresses prejudice against a protected characteristic",
        "Prejudice refers to preconceived views not based on reason. Protected characteristics include gender, ethnicity, religion, sexual orientation, and similar characteristics.",
    )
    threat = "threat", "Contains a threat against a person or persons"
    misleading = "misleading", "Contains text which is incorrect or misleading"
    helpful = "helpful", "Completes the task to a high standard"
    creative = "creative", "Expresses creativity in responding to the task"


class TextLabels(Interaction):
    """A set of labels for a piece of text."""

    type: Literal["text_labels"] = "text_labels"
    text: str
    labels: dict[TextLabel, float]
    message_id: UUID

    @property
    def has_message_id(self) -> bool:
        """Whether this TextLabels has a message_id."""
        return bool(self.message_id)

    # check that each label value is between 0 and 1
    @pydantic.validator("labels")
    def check_label_values(cls, v):
        for key, value in v.items():
            if not (0 <= value <= 1):
                raise ValueError(f"Label values must be between 0 and 1, got {value} for {key}.")
        return v


AnyInteraction = Union[
    TextReplyToMessage,
    MessageRating,
    MessageRanking,
    TextLabels,
]


class SystemStats(BaseModel):
    all: int = 0
    active: int = 0
    deleted: int = 0
    message_trees: int = 0


class UserScore(BaseModel):
    ranking: int
    user_id: UUID
    username: str
    display_name: str
    score: int


class LeaderboardStats(BaseModel):
    leaderboard: List[UserScore]


class OasstErrorResponse(BaseModel):
    """The format of an error response from the OASST API."""

    error_code: OasstErrorCode
    message: str
