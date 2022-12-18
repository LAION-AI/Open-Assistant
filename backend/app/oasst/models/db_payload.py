# -*- coding: utf-8 -*-
from typing import Literal

from oasst.models.payload_column_type import payload_type
from oasst.schemas import protocol as protocol_schema
from pydantic import BaseModel


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
    hint: str


@payload_type
class UserReplyPayload(TaskPayload):
    type: Literal["user_reply"] = "user_reply"
    conversation: protocol_schema.Conversation
    hint: str | None


@payload_type
class AssistantReplyPayload(TaskPayload):
    type: Literal["assistant_reply"] = "assistant_reply"
    conversation: protocol_schema.Conversation


@payload_type
class PostPayload(BaseModel):
    text: str


@payload_type
class ReactionPayload(BaseModel):
    type: str


@payload_type
class RatingReactionPayload(ReactionPayload):
    type: Literal["post_rating"] = "post_rating"
    rating: str


@payload_type
class RankingReactionPayload(ReactionPayload):
    type: Literal["post_ranking"] = "post_ranking"
    ranking: list[int]


@payload_type
class RankConversationRepliesPayload(TaskPayload):
    conversation: protocol_schema.Conversation  # the conversation so far
    replies: list[str]


@payload_type
class RankInitialPromptsPayload(TaskPayload):
    """A task to rank a set of initial prompts."""

    type: Literal["rank_initial_prompts"] = "rank_initial_prompts"
    prompts: list[str]


@payload_type
class RankUserRepliesPayload(RankConversationRepliesPayload):
    """A task to rank a set of user replies to a conversation."""

    type: Literal["rank_user_replies"] = "rank_user_replies"


@payload_type
class RankAssistantRepliesPayload(RankConversationRepliesPayload):
    """A task to rank a set of assistant replies to a conversation."""

    type: Literal["rank_assistant_replies"] = "rank_assistant_replies"
