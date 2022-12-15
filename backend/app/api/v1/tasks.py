# -*- coding: utf-8 -*-
from typing import Any, List
from uuid import UUID

from app.api import deps
from app.schemas import protocol as protocol_schema
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from loguru import logger
from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


@router.post("/", response_model=List[protocol_schema.SummarizeStoryTask])  # work with Union once more types are added
def request_task(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    request: protocol_schema.GenericTaskRequest,  # work with Union once more types are added
) -> Any:
    """
    Create new task.
    """
    deps.api_auth(api_key, db)

    # TODO: Create a task and store it in the database.

    match (request.type):
        case "generic":
            # here we create a task at random (and store it in the database)
            logger.info("Frontend requested a generic task.")
            task = protocol_schema.SummarizeStoryTask(
                story="This is a story. A very long story. So long, it needs to be summarized.",
            )

        case _:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid request type.",
            )
    if request.user_id is not None:
        task.addressed_users = [request.user_id]

    return [task]


@router.post("/{task_id}/ack")
def acknowledge_task(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    task_id: UUID,
    response: protocol_schema.PostCreatedTaskResponse,
) -> Any:
    """
    The frontend acknowledges a task.
    """
    deps.api_auth(api_key, db)

    match (response.type):
        case "post_created":
            logger.info(f"Frontend acknowledged {task_id=} and created {response.post_id=}.")
            # here we would store the post id in the database for the task
        case _:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid response type.",
            )

    return {}


@router.post("/interaction")
def post_interaction(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.TextReplyToPost,
) -> Any:
    """
    The frontend reports an interaction.
    """
    deps.api_auth(api_key, db)

    response = []
    match (interaction.type):
        case "text_reply_to_post":
            logger.info(
                f"Frontend reports text reply to {interaction.post_id=} with {interaction.text=} by {interaction.user_id=}."
            )
            # here we would store the text reply in the database
            response.append(
                protocol_schema.TaskDone(
                    reply_to_post_id=interaction.user_post_id,
                    addressed_users=[interaction.user_id],
                )
            )
        case _:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid response type.",
            )

    return response
