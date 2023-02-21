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
    auth_method: Literal["discord", "local", "system"]


class Account(BaseModel):
    id: UUID
    provider: str
    provider_account_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class FrontEndUser(User):
    user_id: UUID
    enabled: bool
    deleted: bool
    notes: str
    created_date: Optional[datetime] = None
    show_on_leaderboard: bool
    streak_days: Optional[int] = None
    streak_last_day_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    tos_acceptance_date: Optional[datetime] = None


class PageResult(BaseModel):
    prev: str | None
    next: str | None
    sort_key: str
    items: list
    order: Literal["asc", "desc"]


class FrontEndUserPage(PageResult):
    items: list[FrontEndUser]


class ConversationMessage(BaseModel):
    """Represents a message in a conversation between the user and the assistant."""

    id: Optional[UUID] = None
    user_id: Optional[UUID]
    frontend_message_id: Optional[str] = None
    text: str
    lang: Optional[str]  # BCP 47
    is_assistant: bool
    emojis: Optional[dict[str, int]] = None
    user_emojis: Optional[list[str]] = None
    user_is_author: Optional[bool] = None


class Conversation(BaseModel):
    """Represents a conversation between the prompter and the assistant."""

    messages: list[ConversationMessage] = []

    def __len__(self):
        return len(self.messages)

    @property
    def is_prompter_turn(self) -> bool:
        if len(self) == 0:
            return True
        last_message = self.messages[-1]
        if last_message.is_assistant:
            return True
        return False


class Message(ConversationMessage):
    parent_id: Optional[UUID]
    created_date: Optional[datetime]
    review_result: Optional[bool]
    review_count: Optional[int]
    deleted: Optional[bool]
    synthetic: Optional[bool]
    model_name: Optional[str]
    message_tree_id: Optional[UUID]
    ranking_count: Optional[int]
    rank: Optional[int]


class MessagePage(PageResult):
    items: list[Message]


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
    lang: Optional[str] = Field(None, nullable=True)  # BCP 47


class TaskAck(BaseModel):
    """The frontend acknowledges that it has received a task and created a message."""

    message_id: str


class TaskNAck(BaseModel):
    """The frontend acknowledges that it has received a task but cannot create a message."""

    reason: str | None = Field(None, nullable=True)


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
    prompts: list[str]  # deprecated, use prompt_messages
    prompt_messages: list[ConversationMessage]


class RankConversationRepliesTask(Task):
    """A task to rank a set of replies to a conversation."""

    type: Literal["rank_conversation_replies"] = "rank_conversation_replies"
    conversation: Conversation  # the conversation so far
    replies: list[str]  # deprecated, use reply_messages
    reply_messages: list[ConversationMessage]
    message_tree_id: UUID
    ranking_parent_id: UUID


class RankPrompterRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of prompter replies to a conversation."""

    type: Literal["rank_prompter_replies"] = "rank_prompter_replies"


class RankAssistantRepliesTask(RankConversationRepliesTask):
    """A task to rank a set of assistant replies to a conversation."""

    type: Literal["rank_assistant_replies"] = "rank_assistant_replies"


class LabelTaskMode(str, enum.Enum):
    """Label task mode that allows frontends to select an appropriate UI."""

    simple = "simple"
    full = "full"


class LabelTaskDisposition(str, enum.Enum):
    """Reason why the task was issued."""

    quality = "quality"
    spam = "spam"


class LabelDescription(BaseModel):
    name: str
    widget: str
    display_text: str
    help_text: Optional[str]


class AbstractLabelTask(Task):
    message_id: UUID
    valid_labels: list[str]
    mandatory_labels: Optional[list[str]]
    mode: Optional[LabelTaskMode]
    disposition: Optional[LabelTaskDisposition]
    labels: Optional[list[LabelDescription]]
    conversation: Conversation  # the conversation so far (labeling -> last message)


class LabelInitialPromptTask(AbstractLabelTask):
    """A task to label an initial prompt."""

    type: Literal["label_initial_prompt"] = "label_initial_prompt"
    prompt: str | None = Field(None, deprecated=True, description="deprecated, use `prompt_message`")


class LabelConversationReplyTask(AbstractLabelTask):
    """A task to label a reply to a conversation."""

    type: Literal["label_conversation_reply"] = "label_conversation_reply"
    reply: str | None = Field(None, deprecated=True, description="deprecated, use last message of `conversation`")


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
    lang: Optional[str]  # BCP 47


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


class LabelWidget(str, enum.Enum):
    yes_no = "yes_no"
    flag = "flag"
    likert = "likert"


class TextLabel(str, enum.Enum):
    """A label for a piece of text."""

    def __new__(cls, label: str, widget: LabelWidget, display_text: str = "", help_text: str = None):
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.widget = widget
        obj.display_text = display_text
        obj.help_text = help_text
        return obj

    # yes/no questions
    spam = "spam", LabelWidget.yes_no, "Seems to be intentionally low-quality or irrelevant"
    fails_task = "fails_task", LabelWidget.yes_no, "Fails to follow the correct instruction / task"

    # flags
    lang_mismatch = (
        "lang_mismatch",
        LabelWidget.flag,
        "Wrong Language",
        "The message is written in a language that differs from the currently selected language.",
    )
    pii = "pii", LabelWidget.flag, "Contains personal identifiable information (PII)"
    not_appropriate = "not_appropriate", LabelWidget.flag, "Inappropriate"
    hate_speech = (
        "hate_speech",
        LabelWidget.flag,
        "Content is abusive or threatening and expresses prejudice against a protected characteristic",
        "Prejudice refers to preconceived views not based on reason. Protected characteristics "
        "include gender, ethnicity, religion, sexual orientation, and similar characteristics.",
    )
    sexual_content = "sexual_content", LabelWidget.flag, "Contains sexual content"
    moral_judgement = "moral_judgement", LabelWidget.flag, "Expresses moral judgement"
    political_content = "political_content", LabelWidget.flag, "Expresses political views"

    # likert
    quality = "quality", LabelWidget.likert, "Overall subjective quality rating of the message"
    toxicity = "toxicity", LabelWidget.likert, "Rude, abusive, profane or insulting content"
    humor = "humor", LabelWidget.likert, "Humorous content including sarcasm"
    helpfulness = "helpfulness", LabelWidget.likert, "Helpfulness of the message"
    creativity = "creativity", LabelWidget.likert, "Creativity"
    violence = "violence", LabelWidget.likert, "Violence/abuse/terrorism/self-harm"


class TextLabels(Interaction):
    """A set of labels for a piece of text."""

    type: Literal["text_labels"] = "text_labels"
    text: str
    labels: dict[TextLabel, float]
    message_id: UUID
    task_id: Optional[UUID]
    is_report: Optional[bool]

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
    rank: Optional[int]
    user_id: UUID
    highlighted: bool = False
    username: str
    auth_method: str
    display_name: str

    leader_score: int = 0

    base_date: Optional[datetime]
    modified_date: Optional[datetime]

    prompts: int = 0
    replies_assistant: int = 0
    replies_prompter: int = 0
    labels_simple: int = 0
    labels_full: int = 0
    rankings_total: int = 0
    rankings_good: int = 0

    accepted_prompts: int = 0
    accepted_replies_assistant: int = 0
    accepted_replies_prompter: int = 0

    reply_ranked_1: int = 0
    reply_ranked_2: int = 0
    reply_ranked_3: int = 0

    streak_last_day_date: Optional[datetime]
    streak_days: Optional[int]
    last_activity_date: Optional[datetime]


class LeaderboardStats(BaseModel):
    time_frame: str
    last_updated: datetime
    leaderboard: List[UserScore]


class TrollScore(BaseModel):
    rank: Optional[int]
    user_id: UUID
    highlighted: bool = False
    username: str
    auth_method: str
    display_name: str
    last_activity_date: Optional[datetime]
    enabled: bool
    deleted: bool
    show_on_leaderboard: bool

    troll_score: int = 0

    base_date: Optional[datetime]
    modified_date: Optional[datetime]

    red_flags: int = 0  # num reported messages of user
    upvotes: int = 0  # num up-voted messages of user
    downvotes: int = 0  # num down-voted messages of user

    spam_prompts: int = 0

    quality: Optional[float] = None
    humor: Optional[float] = None
    toxicity: Optional[float] = None
    violence: Optional[float] = None
    helpfulness: Optional[float] = None

    spam: int = 0
    lang_mismach: int = 0
    not_appropriate: int = 0
    pii: int = 0
    hate_speech: int = 0
    sexual_content: int = 0
    political_content: int = 0


class TrollboardStats(BaseModel):
    time_frame: str
    last_updated: datetime
    trollboard: List[TrollScore]


class OasstErrorResponse(BaseModel):
    """The format of an error response from the OASST API."""

    error_code: OasstErrorCode
    message: str


class EmojiCode(str, enum.Enum):
    thumbs_up = "+1"  # 👍
    thumbs_down = "-1"  # 👎
    red_flag = "red_flag"  # 🚩
    hundred = "100"  # 💯
    rofl = "rofl"  # 🤣
    clap = "clap"  # 👏
    diamond = "diamond"  # 💎
    heart_eyes = "heart_eyes"  # 😍
    disappointed = "disappointed"  # 😞
    poop = "poop"  # 💩
    skull = "skull"  # 💀

    # skip task system uses special emoji codes
    skip_reply = "_skip_reply"
    skip_ranking = "_skip_ranking"
    skip_labeling = "_skip_labeling"


class EmojiOp(str, enum.Enum):
    togggle = "toggle"
    add = "add"
    remove = "remove"


class MessageEmojiRequest(BaseModel):
    user: User
    op: EmojiOp = EmojiOp.togggle
    emoji: EmojiCode


class CreateFrontendUserRequest(User):
    show_on_leaderboard: bool = True
    enabled: bool = True
    tos_acceptance: Optional[bool] = None
    notes: Optional[str] = None


class CachedStatsName(str, enum.Enum):
    human_messages_by_lang = "human_messages_by_lang"
    human_messages_by_role = "human_messages_by_role"
    message_trees_by_state = "message_trees_by_state"
    message_trees_states_by_lang = "message_trees_states_by_lang"
    users_accepted_tos = "users_accepted_tos"


class CachedStatsResponse(BaseModel):
    name: CachedStatsName | str
    last_updated: datetime
    stats: dict | list


class AllCachedStatsResponse(BaseModel):
    stats_by_name: dict[CachedStatsName | str, CachedStatsResponse]
