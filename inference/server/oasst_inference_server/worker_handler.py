import datetime

import fastapi
import sqlmodel
import websockets.exceptions
from fastapi import Depends
from loguru import logger
from oasst_inference_server import chat_repository, deps, models, queueing, worker_handler
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from sqlalchemy.sql.functions import random as sql_random

WSException = (
    websockets.exceptions.WebSocketException,
    websockets.exceptions.ConnectionClosedError,
    fastapi.WebSocketException,
    fastapi.WebSocketDisconnect,
)


class WorkerError(Exception):
    def __init__(
        self,
        message: str,
        did_work: bool,
        original_exception: Exception | None = None,
    ):
        super().__init__(message)
        self.did_work = did_work
        self.original_exception = original_exception


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


def get_worker_id(
    api_key: str = Depends(get_api_key),
    protocol_version: str = Depends(get_protocol_version),
    session: sqlmodel.Session = Depends(deps.create_session),
) -> models.DbWorker:
    logger.info(f"get_worker: {api_key=}, {protocol_version=}")
    worker = session.exec(sqlmodel.select(models.DbWorker).where(models.DbWorker.api_key == api_key)).one_or_none()
    if worker is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return worker.id


async def send_work_request(
    websocket: fastapi.WebSocket,
    work_request: inference.WorkRequest,
):
    return await websocket.send_text(work_request.json())


async def receive_work_response_packet(
    websocket: fastapi.WebSocket,
) -> inference.WorkResponsePacket:
    return inference.WorkResponsePacket.parse_raw(await websocket.receive_text())


async def receive_worker_config(
    websocket: fastapi.WebSocket,
) -> inference.WorkerConfig:
    return inference.WorkerConfig.parse_raw(await websocket.receive_text())


def get_worker(
    worker_id: str = Depends(get_worker_id),
    session: sqlmodel.Session = Depends(deps.create_session),
    with_for_update: bool = False,
) -> models.DbWorker:
    query = sqlmodel.select(models.DbWorker).where(models.DbWorker.id == worker_id)
    if with_for_update:
        query = query.with_for_update()
    worker = session.exec(query).one()
    return worker


def find_compliance_work_request_message(
    session: sqlmodel.Session, worker_config: inference.WorkerConfig, worker_id: str
) -> models.DbMessage | None:
    compat_hash = worker_config.compat_hash
    message = session.exec(
        sqlmodel.select(models.DbMessage)
        .where(
            models.DbMessage.role == "assistant",
            models.DbMessage.state == inference.MessageState.complete,
            models.DbMessage.worker_compat_hash == compat_hash,
            models.DbMessage.worker_id != worker_id,
        )
        .order_by(sql_random())
    ).first()
    return message


def should_do_compliance_check(session: sqlmodel.Session, worker_id: str) -> bool:
    worker = get_worker(worker_id, session)
    if worker.in_compliance_check:
        return False
    if worker.next_compliance_check is None:
        return True
    return worker.next_compliance_check < datetime.datetime.utcnow()


async def run_compliance_check(websocket: fastapi.WebSocket, worker_id: str, worker_config: inference.WorkerConfig):
    with deps.manual_create_session() as session:
        try:
            worker = get_worker(worker_id, session, with_for_update=True)
            if worker.in_compliance_check:
                logger.info(f"Worker {worker.id} is already in compliance check")
                return
            worker.in_compliance_check = True
        finally:
            session.commit()

    logger.info(f"Running compliance check for worker {worker_id}")

    with deps.manual_create_session() as session:
        try:
            message = find_compliance_work_request_message(session, worker_config, worker_id)
            if message is None:
                logger.warning(
                    f"Could not find message for compliance check for worker {worker_id} with config {worker_config}"
                )
                return

            compliance_work_request = worker_handler.build_work_request(message)

            logger.info(f"Found work request for compliance check for worker {worker_id}: {compliance_work_request}")
            await send_work_request(websocket, compliance_work_request)
            response = None
            while True:
                response = await receive_work_response_packet(websocket)
                if response.error is not None:
                    logger.warning(f"Worker {worker_id} errored during compliance check: {response.error}")
                    return
                if response.is_end:
                    break
            if response is None:
                logger.warning(f"Worker {worker_id} did not respond to compliance check")
                return
            passes = response.generated_text.text == message.content
            logger.info(f"Worker {worker_id} passed compliance check: {passes}")

        finally:
            worker = get_worker(worker_id, session, with_for_update=True)
            worker.next_compliance_check = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=settings.compliance_check_interval
            )
            worker.in_compliance_check = False
            logger.info(f"set next compliance check for worker {worker_id} to {worker.next_compliance_check}")
            session.commit()


async def maybe_do_compliance_check(websocket, worker_id, worker_config):
    with deps.manual_create_session() as session:
        should_check = should_do_compliance_check(session, worker_id)
    if should_check:
        logger.info(f"Worker {worker_id} needs compliance check")
        await run_compliance_check(websocket, worker_id, worker_config)


async def handle_worker(websocket: fastapi.WebSocket, worker_id: str = Depends(get_worker_id)):
    logger.info(f"handle_worker: {worker_id=}")
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    worker_compat_hash = worker_config.compat_hash
    work_queue = queueing.work_queue(deps.redis_client, worker_compat_hash)
    try:
        while True:
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                raise WSException("Worker disconnected")

            if settings.do_compliance_checks:
                await maybe_do_compliance_check(websocket, worker_id, worker_config)

            item = await work_queue.dequeue()
            if item is None:
                continue
            else:
                _, message_id = item

            await perform_work(
                websocket=websocket,
                work_queue=work_queue,
                message_id=message_id,
                worker_id=worker_id,
                worker_config=worker_config,
            )

    except WSException:
        logger.warning(f"Websocket closed for worker {worker_id}")
    except Exception as e:
        logger.exception(f"Error while handling worker {worker_id}: {str(e)}")


def build_work_request(
    message: models.DbMessage,
) -> inference.WorkRequest:
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


async def perform_work(
    *,
    websocket: fastapi.WebSocket,
    work_queue: queueing.RedisQueue,
    message_id: str,
    worker_id: str,
    worker_config: inference.WorkerConfig,
):
    with deps.manual_create_session() as session:
        cr = chat_repository.ChatRepository(session)

        message = cr.start_work(
            message_id=message_id,
            worker_id=worker_id,
            worker_config=worker_config,
        )
        work_request = build_work_request(message)

        logger.info(f"Created {work_request=} with {len(work_request.thread.messages)=}")
        try:
            await send_work_request(websocket, work_request)
        except WSException:
            cr.reset_work(message_id)
            await work_queue.enqueue(message_id)
            raise WorkerError("Worker disconnected while sending work request", did_work=False)

    logger.debug(f"Sent {work_request=} to worker.")

    message_queue = queueing.message_queue(
        deps.redis_client,
        message_id=message_id,
    )

    try:
        response_packet = None
        try:
            while True:
                response_packet = await receive_work_response_packet(websocket)
                await message_queue.enqueue(response_packet.json())
                if response_packet.error is not None:
                    raise WorkerError(f"Worker errored: {response_packet.error}", did_work=True)
                if response_packet.is_end:
                    logger.debug(f"Received {response_packet=} from worker. Ending.")
                    break
        except WSException:
            logger.exception(f"Websocket closed during handling of {message_id=}")
            if response_packet is not None:
                raise WorkerError("Worker disconnected while receiving work response", did_work=True)
            else:
                raise WorkerError("Worker disconnected while receiving work response", did_work=False)
        if response_packet is None:
            raise WorkerError("Worker did not respond", did_work=False)

        logger.info(f"Message {message_id=} is complete.")
        assert response_packet.is_end, "Response packet is not end packet"
        with deps.manual_chat_repository() as cr:
            cr.complete_work(message_id, response_packet.generated_text.text)

    except WorkerError as e:
        with deps.manual_chat_repository() as cr:
            if e.did_work:
                logger.warning(f"Marking {message_id=} as pending since no work was done.")
                cr.reset_work(message_id)
                await work_queue.enqueue(message_id)
            else:
                logger.warning(f"Aborting {message_id=}")
                cr.abort_work(message_id, reason=str(e))
        raise
    except Exception as e:
        logger.exception(f"Error handling {message_id=}")
        cr.abort_work(message_id, reason=str(e))
        raise WorkerError("Error handling chat", did_work=True)
