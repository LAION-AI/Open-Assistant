from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.prompt_repository import PromptRepository, TaskRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.user_repository import UserRepository
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.post(
    "/",
    response_model=protocol_schema.AnyTask,
    dependencies=[
        Depends(deps.UserRateLimiter(times=100, minutes=5)),
        Depends(deps.APIClientRateLimiter(times=10_000, minutes=1)),
    ],
)  # work with Union once more types are added
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
        pr = PromptRepository(db, api_client, client_user=request.user)
        pr.ensure_user_is_enabled()

        tm = TreeManager(db, pr)
        task, message_tree_id, parent_message_id = tm.next_task(desired_task_type=request.type, lang=request.lang)
        pr.task_repository.store_task(task, message_tree_id, parent_message_id, request.collective)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to generate task..")
        raise OasstError("Failed to generate task.", OasstErrorCode.TASK_GENERATION_FAILED)
    return task


@router.post("/availability", response_model=dict[protocol_schema.TaskRequestType, int])
def tasks_availability(
    *,
    user: Optional[protocol_schema.User] = None,
    lang: Optional[str] = "en",
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
):
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, client_user=user)
        tm = TreeManager(db, pr)
        return tm.determine_task_availability(lang)

    except OasstError:
        raise
    except Exception:
        logger.exception("Task availability query failed.")
        raise OasstError("Task availability query failed.", OasstErrorCode.TASK_AVAILABILITY_QUERY_FAILED)


@router.post("/{task_id}/ack", response_model=None, status_code=HTTP_204_NO_CONTENT)
def tasks_acknowledge(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    task_id: UUID,
    ack_request: protocol_schema.TaskAck,
) -> None:
    """
    The frontend acknowledges a task.
    """

    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, frontend_user=frontend_user)

        # here we store the message id in the database for the task
        logger.info(f"Frontend acknowledges task {task_id=}, {ack_request=}.")
        pr.task_repository.bind_frontend_message_id(task_id=task_id, frontend_message_id=ack_request.message_id)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to acknowledge task.")
        raise OasstError("Failed to acknowledge task.", OasstErrorCode.TASK_ACK_FAILED)


@router.post("/{task_id}/nack", response_model=None, status_code=HTTP_204_NO_CONTENT)
def tasks_acknowledge_failure(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    task_id: UUID,
    nack_request: protocol_schema.TaskNAck,
) -> None:
    """
    The frontend reports failure to implement a task.
    """

    try:
        logger.info(f"Frontend reports failure to implement task {task_id=}, {nack_request=}.")
        api_client = deps.api_auth(api_key, db)
        pr = PromptRepository(db, api_client, frontend_user=frontend_user)
        pr.task_repository.acknowledge_task_failure(task_id)
    except (KeyError, RuntimeError):
        logger.exception("Failed to not acknowledge task.")
        raise OasstError("Failed to not acknowledge task.", OasstErrorCode.TASK_NACK_FAILED)


@router.post("/interaction", response_model=protocol_schema.TaskDone)
async def tasks_interaction(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.AnyInteraction,
) -> Any:
    """
    The frontend reports an interaction.
    """

    @managed_tx_function(CommitMode.COMMIT)
    async def interaction_tx(session: deps.Session):
        api_client = deps.api_auth(api_key, db)
        pr = PromptRepository(db, api_client, client_user=interaction.user)
        tm = TreeManager(db, pr)
        ur = UserRepository(db, api_client)
        task = await tm.handle_interaction(interaction)
        match (type(task)):
            case protocol_schema.TaskDone:
                ur.update_user_last_activity(client_user=interaction.user)
        return task

    try:
        return await interaction_tx()
    except OasstError:
        raise
    except Exception:
        logger.exception("Interaction request failed.")
        raise OasstError("Interaction request failed.", OasstErrorCode.TASK_INTERACTION_REQUEST_FAILED)


@router.post("/close", response_model=protocol_schema.TaskDone)
def close_collective_task(
    close_task_request: protocol_schema.TaskClose,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
):
    api_client = deps.api_auth(api_key, db)
    tr = TaskRepository(db, api_client)
    tr.close_task(close_task_request.message_id)
    return protocol_schema.TaskDone()
