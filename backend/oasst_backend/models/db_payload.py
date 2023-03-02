from typing import Literal, Optional
from uuid import UUID

from oasst_backend.models.payload_column_type import payload_type
from oasst_shared.schemas import protocol as protocol_schema
from pydantic import BaseModel, Field


@payload_type
class TaskPayload(BaseModel):
    type: str


@payload_type
class SummarizationStoryPayload(TaskPayload):
    type: Literal["summarize_story"] = "summarize_story"
    story: str


@payload_type
class RateSummaryPayload(TaskPayload):
    type: Literal["rate_summary"] = "rate_summary"
    full_text: str
    summary: str
    scale: protocol_schema.RatingScale


@payload_type
class InitialPromptPayload(TaskPayload):
    type: Literal["initial_prompt"] = "initial_prompt"
    hint: str | None


@payload_type
class PrompterReplyPayload(TaskPayload):
    type: Literal["prompter_reply"] = "prompter_reply"
    conversation: protocol_schema.Conversation
    hint: str | None


@payload_type
class AssistantReplyPayload(TaskPayload):
    type: Literal["assistant_reply"] = "assistant_reply"
    conversation: protocol_schema.Conversation


@payload_type
class MessagePayload(BaseModel):
    text: str


@payload_type
class ReactionPayload(BaseModel):
    type: str


@payload_type
class RatingReactionPayload(ReactionPayload):
    type: Literal["message_rating"] = "message_rating"
    rating: str


@payload_type
class RankingReactionPayload(ReactionPayload):
    type: Literal["message_ranking"] = "message_ranking"
    ranking: list[int]
    ranked_message_ids: list[UUID]
    ranking_parent_id: Optional[UUID]
    message_tree_id: Optional[UUID]
    not_rankable: Optional[bool]  # all options flawed, factually incorrect or unacceptable


@payload_type
class RankConversationRepliesPayload(TaskPayload):
    conversation: protocol_schema.Conversation  # the conversation so far
    reply_messages: list[protocol_schema.ConversationMessage]
    ranking_parent_id: Optional[UUID]
    message_tree_id: Optional[UUID]
    reveal_synthetic: Optional[bool]


@payload_type
class RankInitialPromptsPayload(TaskPayload):
    """A task to rank a set of initial prompts."""

    type: Literal["rank_initial_prompts"] = "rank_initial_prompts"
    prompt_messages: list[protocol_schema.ConversationMessage]


@payload_type
class RankPrompterRepliesPayload(RankConversationRepliesPayload):
    """A task to rank a set of prompter replies to a conversation."""

    type: Literal["rank_prompter_replies"] = "rank_prompter_replies"


@payload_type
class RankAssistantRepliesPayload(RankConversationRepliesPayload):
    """A task to rank a set of assistant replies to a conversation."""

    type: Literal["rank_assistant_replies"] = "rank_assistant_replies"


@payload_type
class LabelInitialPromptPayload(TaskPayload):
    """A task to label an initial prompt."""

    type: Literal["label_initial_prompt"] = "label_initial_prompt"
    message_id: UUID
    prompt: str
    valid_labels: list[str]
    mandatory_labels: Optional[list[str]]
    mode: Optional[protocol_schema.LabelTaskMode]


@payload_type
class LabelConversationReplyPayload(TaskPayload):
    """A task to label a conversation reply."""

    message_id: UUID
    conversation: protocol_schema.Conversation
    reply: Optional[str] = Field(None, deprecated=True, description="deprecated")
    reply_message: Optional[protocol_schema.ConversationMessage] = Field(
        None, deprecated=True, description="deprecated"
    )
    valid_labels: list[str]
    mandatory_labels: Optional[list[str]]
    mode: Optional[protocol_schema.LabelTaskMode]


@payload_type
class LabelPrompterReplyPayload(LabelConversationReplyPayload):
    """A task to label a prompter reply."""

    type: Literal["label_prompter_reply"] = "label_prompter_reply"


@payload_type
class LabelAssistantReplyPayload(LabelConversationReplyPayload):
    """A task to label an assistant reply."""

    type: Literal["label_assistant_reply"] = "label_assistant_reply"
