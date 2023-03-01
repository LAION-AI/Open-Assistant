import datetime
import enum
import uuid

import fastapi
import pydantic
import sqlmodel
import websockets.exceptions
from fastapi import Depends
from loguru import logger
from oasst_inference_server import chat_repository, deps, models, queueing, worker_handler
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from sqlalchemy.sql.functions import random as sql_random
from sqlmodel import not_, or_

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


class WorkerSessionStatus(str, enum.Enum):
    waiting = "waiting"
    working = "working"
    compliance_check = "compliance_check"


class WorkerSession(pydantic.BaseModel):
    session_id: str
    worker_id: str
    config: inference.WorkerConfig
    status: WorkerSessionStatus = WorkerSessionStatus.waiting


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


def add_worker_connect_event(
    session: sqlmodel.Session,
    worker_id: str,
    worker_config: inference.WorkerConfig,
):
    event = models.DbWorkerEvent(
        worker_id=worker_id,
        event_type=models.WorkerEventType.connect,
        worker_config=worker_config,
    )
    session.add(event)
    session.commit()


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
        compliance_check = models.DbWorkerComplianceCheck(worker_id=worker_id)

        try:
            message = find_compliance_work_request_message(session, worker_config, worker_id)
            if message is None:
                logger.warning(
                    f"Could not find message for compliance check for worker {worker_id} with config {worker_config}"
                )
                return

            compliance_check.compare_worker_id = message.worker_id
            compliance_work_request = worker_handler.build_work_request(message)

            logger.info(f"Found work request for compliance check for worker {worker_id}: {compliance_work_request}")
            await send_work_request(websocket, compliance_work_request)
            response = None
            while True:
                response = await receive_work_response_packet(websocket)
                if response.error is not None:
                    compliance_check.responded = True
                    compliance_check.error = response.error
                    logger.warning(f"Worker {worker_id} errored during compliance check: {response.error}")
                    return
                if response.is_end:
                    break
            if response is None:
                logger.warning(f"Worker {worker_id} did not respond to compliance check")
                return
            compliance_check.responded = True
            passes = response.generated_text.text == message.content
            compliance_check.passed = passes
            logger.info(f"Worker {worker_id} passed compliance check: {passes}")

        finally:
            compliance_check.end_time = datetime.datetime.utcnow()
            session.add(compliance_check)
            worker = get_worker(worker_id, session, with_for_update=True)
            worker.next_compliance_check = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=settings.compliance_check_interval
            )
            worker.in_compliance_check = False
            logger.info(f"set next compliance check for worker {worker_id} to {worker.next_compliance_check}")
            session.commit()


async def maybe_do_compliance_check(websocket, worker_id, worker_config, worker_session_id):
    with deps.manual_create_session() as session:
        should_check = should_do_compliance_check(session, worker_id)
    if should_check:
        logger.info(f"Worker {worker_id} needs compliance check")
        try:
            await update_worker_session_status(worker_session_id, WorkerSessionStatus.compliance_check)
            await run_compliance_check(websocket, worker_id, worker_config)
        finally:
            await update_worker_session_status(worker_session_id, WorkerSessionStatus.waiting)


async def store_worker_session(
    worker_session_id: str,
    worker_id: str,
    worker_config: inference.WorkerConfig,
):
    worker_session = WorkerSession(
        session_id=worker_session_id,
        worker_id=worker_id,
        config=worker_config,
        status=WorkerSessionStatus.waiting,
    )
    await deps.redis_client.set(f"worker_session:{worker_session_id}", worker_session.json())


async def delete_worker_session(worker_session_id: str):
    await deps.redis_client.delete(f"worker_session:{worker_session_id}")


async def update_worker_session_status(
    worker_session_id: str,
    status: WorkerSessionStatus,
):
    worker_session = WorkerSession.parse_raw(await deps.redis_client.get(f"worker_session:{worker_session_id}"))
    worker_session.status = status
    await deps.redis_client.set(f"worker_session:{worker_session_id}", worker_session.json())


async def handle_worker(websocket: fastapi.WebSocket, worker_id: str = Depends(get_worker_id)):
    logger.info(f"handle_worker: {worker_id=}")
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    worker_compat_hash = worker_config.compat_hash
    work_queue = queueing.work_queue(deps.redis_client, worker_compat_hash)
    worker_session_id = str(uuid.uuid4())
    try:
        with deps.manual_create_session() as session:
            add_worker_connect_event(session=session, worker_id=worker_id, worker_config=worker_config)
        await store_worker_session(worker_session_id, worker_id, worker_config)
        while True:
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                raise WSException("Worker disconnected")

            if settings.do_compliance_checks:
                await maybe_do_compliance_check(websocket, worker_id, worker_config, worker_session_id)

            item = await work_queue.dequeue()
            if item is None:
                continue
            else:
                _, message_id = item

            try:
                await update_worker_session_status(worker_session_id, WorkerSessionStatus.working)
                await perform_work(
                    websocket=websocket,
                    work_queue=work_queue,
                    message_id=message_id,
                    worker_id=worker_id,
                    worker_config=worker_config,
                )
            finally:
                await update_worker_session_status(worker_session_id, WorkerSessionStatus.waiting)

    except WSException:
        logger.warning(f"Websocket closed for worker {worker_id}")
    except Exception as e:
        logger.exception(f"Error while handling worker {worker_id}: {str(e)}")
    finally:
        logger.info(f"Worker {worker_id} disconnected")
        await delete_worker_session(worker_session_id)


async def list_worker_sessions() -> list[inference.WorkerConfig]:
    redis_client = deps.redis_client
    try:
        worker_configs = []
        async for key in redis_client.scan_iter("worker_session:*"):
            worker_config_json = await redis_client.get(key)
            worker_config = inference.WorkerConfig.parse_raw(worker_config_json)
            worker_configs.append(worker_config)
    except Exception as e:
        logger.exception(f"Error while listing worker sessions: {str(e)}")
        raise
    return worker_configs


async def clear_worker_sessions():
    redis_client = deps.redis_client
    try:
        logger.info("Clearing worker sessions")
        async for key in redis_client.scan_iter("worker_session:*"):
            await redis_client.getdel(key)
    except Exception as e:
        logger.exception(f"Error while clearing worker sessions: {str(e)}")
        raise


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


async def compute_worker_compliance_score(worker_id: str) -> float:
    """
    Compute a float between 0 and 1 (inclusive) representing the compliance score of the worker.
    Workers are rewarded for passing compliance checks, and penalised for failing to respond to a check, erroring during a check, or failing a check.
    In-progress checks are ignored.
    """
    with deps.manual_create_session() as session:
        worker_checks: list[models.DbWorkerComplianceCheck] = session.exec(
            sqlmodel.select(models.DbWorkerComplianceCheck).where(
                or_(
                    models.DbWorkerComplianceCheck.worker_id == worker_id,
                    models.DbWorkerComplianceCheck.compare_worker_id == worker_id,
                ),
                not_(models.DbWorkerComplianceCheck.end_time.is_(None)),
            )
        ).all()

        # Rudimentary scoring algorithm, we may want to add weightings or other factors
        total_count = len(worker_checks)

        checked = [c for c in worker_checks if c.worker_id == worker_id]
        compared = [c for c in worker_checks if c.compare_worker_id == worker_id]

        pass_count = sum(1 for _ in filter(lambda c: c.passed, checked))
        error_count = sum(1 for _ in filter(lambda c: c.error is not None, checked))
        no_response_count = sum(1 for _ in filter(lambda c: not c.responded, checked))

        compare_fail_count = sum(1 for _ in filter(lambda c: not c.passed, compared))
        fail_count = len(checked) - pass_count - error_count - no_response_count

        return (fail_count + compare_fail_count) / total_count
