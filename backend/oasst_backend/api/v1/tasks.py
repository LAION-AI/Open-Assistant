# -*- coding: utf-8 -*-
import random
from typing import Any, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session

router = APIRouter()


def generate_task(
    request: protocol_schema.TaskRequest, pr: PromptRepository
) -> Tuple[protocol_schema.Task, Optional[UUID], Optional[UUID]]:
    message_tree_id = None
    parent_message_id = None

    match request.type:
        case protocol_schema.TaskRequestType.random:
            logger.info("Frontend requested a random task.")
            while request.type == protocol_schema.TaskRequestType.random:
                disabled_tasks = (
                    protocol_schema.TaskRequestType.summarize_story,
                    protocol_schema.TaskRequestType.rate_summary,
                )
                request.type = random.choice(
                    tuple(set(protocol_schema.TaskRequestType).difference(disabled_tasks))
                ).value
            return generate_task(request, pr)

        # AKo: Summary tasks are currently disabled/supported, we focus on the conversation tasks.

        # case protocol_schema.TaskRequestType.summarize_story:
        #     logger.info("Generating a SummarizeStoryTask.")
        #     task = protocol_schema.SummarizeStoryTask(
        #         story="This is a story. A very long story. So long, it needs to be summarized.",
        #     )
        # case protocol_schema.TaskRequestType.rate_summary:
        #     logger.info("Generating a RateSummaryTask.")
        #     task = protocol_schema.RateSummaryTask(
        #         full_text="This is a story. A very long story. So long, it needs to be summarized.",
        #         summary="This is a summary.",
        #         scale=protocol_schema.RatingScale(min=1, max=5),
        #     )

        case protocol_schema.TaskRequestType.initial_prompt:
            logger.info("Generating an InitialPromptTask.")
            task = protocol_schema.InitialPromptTask(
                hint="Ask the assistant about a current event."  # this is optional
            )
        case protocol_schema.TaskRequestType.user_reply:
            logger.info("Generating a UserReplyTask.")
            messages = pr.fetch_random_conversation("assistant")
            messages = [
                protocol_schema.ConversationMessage(text=m.payload.payload.text, is_assistant=(m.role == "assistant"))
                for m in messages
            ]

            task = protocol_schema.UserReplyTask(conversation=protocol_schema.Conversation(messages=messages))
            message_tree_id = messages[-1].message_tree_id
            parent_message_id = messages[-1].id
        case protocol_schema.TaskRequestType.assistant_reply:
            logger.info("Generating a AssistantReplyTask.")
            messages = pr.fetch_random_conversation("user")
            messages = [
                protocol_schema.ConversationMessage(text=m.payload.payload.text, is_assistant=(m.role == "assistant"))
                for m in messages
            ]

            task = protocol_schema.AssistantReplyTask(conversation=protocol_schema.Conversation(messages=messages))
            message_tree_id = messages[-1].message_tree_id
            parent_message_id = messages[-1].id
        case protocol_schema.TaskRequestType.rank_initial_prompts:
            logger.info("Generating a RankInitialPromptsTask.")

            messages = pr.fetch_random_initial_prompts()
            task = protocol_schema.RankInitialPromptsTask(prompts=[m.payload.payload.text for m in messages])
        case protocol_schema.TaskRequestType.rank_user_replies:
            logger.info("Generating a RankUserRepliesTask.")
            conversation, replies = pr.fetch_multiple_random_replies(message_role="assistant")

            messages = [
                protocol_schema.ConversationMessage(
                    text=p.payload.payload.text,
                    is_assistant=(p.role == "assistant"),
                )
                for p in conversation
            ]
            replies = [p.payload.payload.text for p in replies]
            task = protocol_schema.RankUserRepliesTask(
                conversation=protocol_schema.Conversation(
                    messages=messages,
                ),
                replies=replies,
            )

        case protocol_schema.TaskRequestType.rank_assistant_replies:
            logger.info("Generating a RankAssistantRepliesTask.")
            conversation, replies = pr.fetch_multiple_random_replies(message_role="user")

            messages = [
                protocol_schema.ConversationMessage(
                    text=p.payload.payload.text,
                    is_assistant=(p.role == "assistant"),
                )
                for p in conversation
            ]
            replies = [p.payload.payload.text for p in replies]
            task = protocol_schema.RankAssistantRepliesTask(
                conversation=protocol_schema.Conversation(messages=messages),
                replies=replies,
            )
        case _:
            raise OasstError("Invalid request type", OasstErrorCode.TASK_INVALID_REQUEST_TYPE)

    logger.info(f"Generated {task=}.")

    return task, message_tree_id, parent_message_id


@router.post("/", response_model=protocol_schema.AnyTask)  # work with Union once more types are added
def request_task(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    request: protocol_schema.TaskRequest,
) -> Any:
    """
    Create new task.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, request.user)
        task, message_tree_id, parent_message_id = generate_task(request, pr)
        pr.store_task(task, message_tree_id, parent_message_id, request.collective)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to generate task..")
        raise OasstError("Failed to generate task.", OasstErrorCode.TASK_GENERATION_FAILED)
    return task


@router.post("/{task_id}/ack")
def acknowledge_task(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    task_id: UUID,
    ack_request: protocol_schema.TaskAck,
) -> Any:
    """
    The frontend acknowledges a task.
    """

    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, user=None)

        # here we store the message id in the database for the task
        logger.info(f"Frontend acknowledges task {task_id=}, {ack_request=}.")
        pr.bind_frontend_message_id(task_id=task_id, message_id=ack_request.message_id)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to acknowledge task.")
        raise OasstError("Failed to acknowledge task.", OasstErrorCode.TASK_ACK_FAILED)
    return {}


@router.post("/{task_id}/nack")
def acknowledge_task_failure(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    task_id: UUID,
    nack_request: protocol_schema.TaskNAck,
) -> Any:
    """
    The frontend reports failure to implement a task.
    """

    try:
        logger.info(f"Frontend reports failure to implement task {task_id=}, {nack_request=}.")
        api_client = deps.api_auth(api_key, db)
        pr = PromptRepository(db, api_client, user=None)
        pr.acknowledge_task_failure(task_id)
    except (KeyError, RuntimeError):
        logger.exception("Failed to not acknowledge task.")
        raise OasstError("Failed to not acknowledge task.", OasstErrorCode.TASK_NACK_FAILED)


@router.post("/interaction")
def message_interaction(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.AnyInteraction,
) -> Any:
    """
    The frontend reports an interaction.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, user=interaction.user)

        match type(interaction):
            case protocol_schema.TextReplyToMessage:
                logger.info(
                    f"Frontend reports text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                )

                # here we store the text reply in the database
                pr.store_text_reply(
                    text=interaction.text, message_id=interaction.message_id, user_message_id=interaction.user_message_id
                )

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRating:
                logger.info(
                    f"Frontend reports rating of {interaction.message_id=} with {interaction.rating=} by {interaction.user=}."
                )

                # here we store the rating in the database
                pr.store_rating(interaction)

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRanking:
                logger.info(
                    f"Frontend reports ranking of {interaction.message_id=} with {interaction.ranking=} by {interaction.user=}."
                )

                # TODO: check if the ranking is valid
                pr.store_ranking(interaction)
                # here we would store the ranking in the database
                return protocol_schema.TaskDone()
            case _:
                raise OasstError("Invalid response type.", OasstErrorCode.TASK_INVALID_RESPONSE_TYPE)
    except OasstError:
        raise
    except Exception:
        logger.exception("Interaction request failed.")
        raise OasstError("Interaction request failed.", OasstErrorCode.TASK_INTERACTION_REQUEST_FAILED)


@router.post("/close")
def close_collective_task(
    close_task_request: protocol_schema.TaskClose,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
):
    api_client = deps.api_auth(api_key, db)
    pr = PromptRepository(db, api_client, user=None)
    pr.close_task(close_task_request.message_id)
    return protocol_schema.TaskDone()
