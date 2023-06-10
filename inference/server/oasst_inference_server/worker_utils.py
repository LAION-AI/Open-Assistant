import enum
import uuid

import fastapi
import pydantic
import sqlalchemy.orm
import sqlmodel
from fastapi import Depends
from loguru import logger
from oasst_inference_server import database, deps, models
from oasst_shared.schemas import inference


class WorkerSessionStatus(str, enum.Enum):
    waiting = "waiting"
    working = "working"
    compliance_check = "compliance_check"


class WorkerSession(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    worker_info: inference.WorkerInfo
    requests_in_flight: int = 0
    metrics: inference.WorkerMetricsInfo | None = None


api_key_header = fastapi.Header(None, alias="X-API-Key")


def get_api_key(api_key: str = api_key_header) -> str:
    if api_key is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    return api_key


protocol_version_header = fastapi.Header(None, alias="X-Protocol-Version")


def get_protocol_version(protocol_version: str = protocol_version_header) -> str:
    if protocol_version != inference.INFERENCE_PROTOCOL_VERSION:
        logger.warning(f"Got worker with incompatible protocol version: {protocol_version}")
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_426_UPGRADE_REQUIRED,
            detail=f"Incompatible protocol version: {protocol_version}. Expected: {inference.INFERENCE_PROTOCOL_VERSION}.",
        )
    return protocol_version


async def get_worker_id(
    api_key: str = Depends(get_api_key),
    protocol_version: str = Depends(get_protocol_version),
) -> models.DbWorker:
    """Get the ID of a worker from its API key and protocol version."""
    logger.info(f"get_worker: {api_key=}, {protocol_version=}")
    query = sqlmodel.select(models.DbWorker).where(models.DbWorker.api_key == api_key)
    async with deps.manual_create_session() as session:
        worker: models.DbWorker = (await session.exec(query)).one_or_none()
    if worker is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return worker.id


async def get_worker(
    worker_id: str = Depends(get_worker_id),
    session: database.AsyncSession = Depends(deps.create_session),
) -> models.DbWorker:
    query = sqlmodel.select(models.DbWorker).where(models.DbWorker.id == worker_id)
    worker = (await session.exec(query)).one()
    return worker


async def send_worker_request(
    websocket: fastapi.WebSocket,
    request: inference.WorkerRequest,
):
    return await websocket.send_text(request.json())


async def receive_worker_response(
    websocket: fastapi.WebSocket,
) -> inference.WorkerResponse:
    return pydantic.parse_raw_as(inference.WorkerResponse, await websocket.receive_text())


async def receive_worker_info(
    websocket: fastapi.WebSocket,
) -> inference.WorkerInfo:
    return inference.WorkerInfo.parse_raw(await websocket.receive_text())


async def store_worker_session(worker_session: WorkerSession):
    await deps.redis_client.set(f"worker_session:{worker_session.id}", worker_session.json())


async def delete_worker_session(worker_session_id: str):
    await deps.redis_client.delete(f"worker_session:{worker_session_id}")
    logger.debug(f"Deleted worker session {worker_session_id}")


async def build_work_request(
    session: database.AsyncSession,
    message_id: str,
) -> inference.WorkRequest:
    """
    Build a work request based on the assistant message associated with the given ID in the database.
    This will build a chat history based on the parents of the assistant message which will form the work request along
    with the work parameters associated with the assistant message.
    """
    query = (
        sqlmodel.select(models.DbMessage)
        .options(
            sqlalchemy.orm.selectinload(models.DbMessage.chat)
            .selectinload(models.DbChat.messages)
            .selectinload(models.DbMessage.reports),
        )
        .where(models.DbMessage.id == message_id)
    )
    message: models.DbMessage = (await session.exec(query)).one()
    chat = message.chat
    msg_dict = chat.get_msg_dict()
    thread_msgs = [msg_dict[message.parent_id]]
    while thread_msgs[-1].parent_id is not None:
        thread_msgs.append(msg_dict[thread_msgs[-1].parent_id])
    thread = inference.Thread(
        messages=[m.to_read() for m in reversed(thread_msgs)],
    )
    return inference.WorkRequest(
        thread=thread,
        parameters=message.work_parameters,
    )
