# -*- coding: utf-8 -*-
import random
from typing import Any
from uuid import UUID

from app.api import deps
from app.prompt_repository import PromptRepository, RateSummaryPayload, TaskPayload
from app.schemas import protocol as protocol_schema
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from loguru import logger
from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


def generate_task(request: protocol_schema.TaskRequest) -> protocol_schema.Task:
    match (request.type):
        case protocol_schema.TaskRequestType.random:
            logger.info("Frontend requested a random task.")
            while request.type == protocol_schema.TaskRequestType.random:
                request.type = random.choice(list(protocol_schema.TaskRequestType)).value
            return generate_task(request)
        case protocol_schema.TaskRequestType.summarize_story:
            logger.info("Generating a SummarizeStoryTask.")
            task = protocol_schema.SummarizeStoryTask(
                story="This is a story. A very long story. So long, it needs to be summarized.",
            )
        case protocol_schema.TaskRequestType.rate_summary:
            logger.info("Generating a RateSummaryTask.")
            task = protocol_schema.RateSummaryTask(
                full_text="This is a story. A very long story. So long, it needs to be summarized.",
                summary="This is a summary.",
                scale=protocol_schema.RatingScale(min=1, max=5),
            )
        case protocol_schema.TaskRequestType.initial_prompt:
            logger.info("Generating an InitialPromptTask.")
            task = protocol_schema.InitialPromptTask(
                hint="Ask the assistant about a current event."  # this is optional
            )
        case protocol_schema.TaskRequestType.user_reply:
            logger.info("Generating a UserReplyTask.")
            task = protocol_schema.UserReplyTask(
                conversation=protocol_schema.Conversation(
                    messages=[
                        protocol_schema.ConversationMessage(
                            text="Hey, assistant, what's going on in the world?",
                            is_assistant=False,
                        ),
                        protocol_schema.ConversationMessage(
                            text="I'm not sure I understood correctly, could you rephrase that?",
                            is_assistant=True,
                        ),
                    ],
                )
            )
        case protocol_schema.TaskRequestType.assistant_reply:
            logger.info("Generating a AssistantReplyTask.")
            task = protocol_schema.AssistantReplyTask(
                conversation=protocol_schema.Conversation(
                    messages=[
                        protocol_schema.ConversationMessage(
                            text="Hey, assistant, write me an English essay about water.",
                            is_assistant=False,
                        ),
                    ],
                )
            )
        case _:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid request type.",
            )
    logger.info(f"Generated {task=}.")
    if request.user is not None:
        task.addressed_user = request.user

    return task


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
        task = generate_task(request)

        pr = PromptRepository(db, api_client, request.user)
        pr.store_task(task)

    except Exception:
        logger.exception("Failed to generate task.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )
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
    pr = PromptRepository(db, api_client, user=None)

    logger.info(f"Frontend acknowledges task {task_id=}, {ack_request=}.")
    # here we store the post id in the database for the task
    try:
        pr.bind_frontend_post_id(task_id=task_id, post_id=ack_request.post_id)
    except Exception as err:
        logger.warning(err)
        raise
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
    deps.api_auth(api_key, db)

    logger.info(f"Frontend reports failure to implement task {task_id=}, {nack_request=}.")
    # here we would store the post id in the database for the task
    return {}


@router.post("/interaction")
def post_interaction(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.AnyInteraction,
) -> Any:
    """
    The frontend reports an interaction.
    """
    api_client = deps.api_auth(api_key, db)
    pr = PromptRepository(db, api_client, user=interaction.user)

    match (type(interaction)):
        case protocol_schema.TextReplyToPost:
            logger.info(
                f"Frontend reports text reply to {interaction.post_id=} with {interaction.text=} by {interaction.user=}."
            )

            work_package = pr.fetch_workpackage_by_postid(interaction.post_id)
            work_payload: TaskPayload = work_package.payload.payload
            logger.info(f"found task work package in db: {work_payload}")

            # here we store the text reply in the database
            # ToDo: role user or agent?
            pr.store_text_reply(interaction, role="unknown")

            return protocol_schema.TaskDone(
                reply_to_post_id=interaction.user_post_id,
                addressed_user=interaction.user,
            )
        case protocol_schema.PostRating:
            logger.info(
                f"Frontend reports rating of {interaction.post_id=} with {interaction.rating=} by {interaction.user=}."
            )
            # check if rating in range

            work_package = pr.fetch_workpackage_by_postid(interaction.post_id)
            work_payload: RateSummaryPayload = work_package.payload.payload
            if (
                type(work_payload) != RateSummaryPayload
                or interaction.rating < work_payload.scale.min
                or interaction.rating > work_payload.scale.max
            ):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid response type.",
                )

            pr.store_rating(interaction)

            # here we would store the rating in the database
            return protocol_schema.TaskDone(
                reply_to_post_id=interaction.post_id,
                addressed_user=interaction.user,
            )
        case _:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid response type.",
            )
