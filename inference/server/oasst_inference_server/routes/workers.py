import asyncio
import datetime
from enum import Enum
from typing import Awaitable, NamedTuple, TypeVar, cast

import fastapi
import pydantic
import websockets.exceptions
from loguru import logger
from oasst_inference_server import chat_repository, database, deps, models, queueing, worker_utils
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference


class WorkerDisconnectException(Exception):
    def __init__(self):
        super().__init__("Worker disconnected")


WSException = (
    websockets.exceptions.WebSocketException,
    websockets.exceptions.ConnectionClosedError,
    fastapi.WebSocketException,
    fastapi.WebSocketDisconnect,
    WorkerDisconnectException,
)

router = fastapi.APIRouter(
    prefix="/workers",
    tags=["workers"],
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


class WorkRequestContainer(pydantic.BaseModel):
    work_request: inference.WorkRequest
    message_id: str
    start_time: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow)
    num_responses: int = 0

    class Config:
        arbitrary_types_allowed = True


WorkRequestContainerMap = dict[str, WorkRequestContainer]


class WorkRequestNotFound(Exception):
    def __init__(self, request_id: str):
        super().__init__(f"Work request not found: {request_id=}")
        self.request_id = request_id


def get_work_request_container(work_request_map: WorkRequestContainerMap, request_id: str) -> WorkRequestContainer:
    if request_id is None:
        raise WorkRequestNotFound(request_id)
    container = work_request_map.get(request_id)
    if container is None:
        raise WorkRequestNotFound(request_id)
    return container


class HandleWorkerContext(NamedTuple):
    """
    Whenever a worker connects to the inference server over a websocket, we create an instance of this class to hold all
    state that is associated with that worker and connection.
    """

    websocket: fastapi.WebSocket
    worker_id: str
    worker_info: inference.WorkerInfo

    work_queue: queueing.RedisQueue

    blocking_work_queue: queueing.RedisQueue

    work_request_map: dict[str, WorkRequestContainer] = dict()

    @property
    def config(self) -> inference.WorkerConfig:
        return self.worker_info.config

    @property
    def worker_compat_hash(self) -> str:
        return self.config.compat_hash

    @property
    def num_requests_in_progress(self) -> int:
        return len(self.work_request_map)

    @classmethod
    async def build(cls, websocket: fastapi.WebSocket, api_key: str, protocol_version: str):
        try:
            worker_utils.get_protocol_version(protocol_version)
            api_key = worker_utils.get_api_key(api_key)
            worker_id = await worker_utils.get_worker_id(api_key=api_key, protocol_version=protocol_version)
        except fastapi.HTTPException as e:
            logger.warning(f"handle_worker: {e.status_code=} {e.detail=}")
            if e.status_code == fastapi.status.HTTP_426_UPGRADE_REQUIRED:
                await worker_utils.send_worker_request(websocket=websocket, request=inference.UpgradeProtocolRequest())
            elif e.status_code == fastapi.status.HTTP_401_UNAUTHORIZED:
                await worker_utils.send_worker_request(websocket=websocket, request=inference.WrongApiKeyRequest())
            try:
                await websocket.close(code=e.status_code, reason=e.detail)
            except Exception:
                pass
            raise fastapi.WebSocketException(e.status_code, e.detail)

        logger.info(f"handle_worker: {worker_id=}")
        worker_info = await worker_utils.receive_worker_info(websocket)
        logger.info(f"handle_worker: {worker_info=}")

        work_queue = queueing.work_queue(deps.redis_client, worker_info.config.compat_hash)

        # Make a new Redis client that we can use for the blocking requests without affecting the non-blocking calls
        redis_client = deps.make_redis_client()
        blocking_work_queue = queueing.work_queue(redis_client, worker_info.config.compat_hash)

        return cls(
            websocket=websocket,
            worker_id=worker_id,
            worker_info=worker_info,
            work_queue=work_queue,
            blocking_work_queue=blocking_work_queue,
        )

    async def close(self):
        try:
            await self.blocking_work_queue.redis_client.close()
        except Exception:
            logger.warning("Error while closing redis client")

        try:
            await self.websocket.close()
        except Exception:
            logger.warning("Error while closing websocket")


class FutureType(str, Enum):
    WORK_REQUEST = "WORK_REQUEST"
    WORKER_RESPONSE = "WORKER_RESPONSE"


AwaitResult = TypeVar("AwaitResult")


class FuturesManager:
    _context: HandleWorkerContext
    _futures: set[asyncio.Future]

    def __init__(self, context: HandleWorkerContext):
        self._context = context
        self._futures = set()

    def ensure_listening_for_work_requests(self):
        requests_in_progress = self._context.num_requests_in_progress
        if requests_in_progress < self._context.config.max_parallel_requests:
            future = self._as_typed_future(
                FutureType.WORK_REQUEST, self._context.blocking_work_queue.dequeue(timeout=0)
            )
            self._futures.add(future)

    def ensure_listening_to_worker_responses(self):
        future = self._as_typed_future(
            FutureType.WORKER_RESPONSE, worker_utils.receive_worker_response(websocket=self._context.websocket)
        )
        self._futures.add(future)

    async def wait_for_event_or_timeout(self):
        completed_futures, pending_futures = await asyncio.wait(
            self._futures, timeout=settings.worker_ping_interval, return_when=asyncio.FIRST_COMPLETED
        )
        self._futures = pending_futures

        return [future.result() for future in completed_futures]

    def cancel_all(self):
        logger.info(f"Cancelling {len(self._futures)} pending futures")
        for ftr in self._futures:
            try:
                ftr.cancel()
            except Exception:
                logger.warning("Error while cancelling pending future")

    def _as_typed_future(self, future_type: FutureType, awaitable: Awaitable[AwaitResult]) -> asyncio.Future:
        async def wrapper():
            result = await awaitable
            return future_type, result

        # Note: important to call the wrapper to create the coroutine
        return asyncio.ensure_future(wrapper())


class SessionManager:
    _context: HandleWorkerContext
    _session: worker_utils.WorkerSession

    def __init__(self, context: HandleWorkerContext):
        self._context = context
        self._session = worker_utils.WorkerSession(
            worker_id=context.worker_id,
            worker_info=context.worker_info,
        )

    async def update(self, metrics: inference.WorkerMetricsInfo | None = None):
        self._session.requests_in_flight = len(self._context.work_request_map)
        if metrics:
            self._session.metrics = metrics
            await worker_utils.store_worker_session(self._session)

    async def _add_worker_connect_event(
        self,
        session: database.AsyncSession,
        worker_id: str,
        worker_info: inference.WorkerInfo,
    ):
        event = models.DbWorkerEvent(
            worker_id=worker_id,
            event_type=models.WorkerEventType.connect,
            worker_info=worker_info,
        )
        session.add(event)
        await session.commit()

    async def init(self):
        async with deps.manual_create_session() as session:
            await self._add_worker_connect_event(
                session=session, worker_id=self._context.worker_id, worker_info=self._context.worker_info
            )
        await worker_utils.store_worker_session(self._session)

    async def close(self):
        try:
            await worker_utils.delete_worker_session(self._session.id)
        except Exception:
            logger.warning("Error while deleting worker session")


async def _handle_work_request(message_id: str, context: HandleWorkerContext, futures: FuturesManager):
    try:
        work_request = await initiate_work_for_message(
            websocket=context.websocket,
            work_queue=context.work_queue,
            message_id=message_id,
            worker_id=context.worker_id,
            worker_config=context.config,
        )
        context.work_request_map[work_request.id] = WorkRequestContainer(
            work_request=work_request, message_id=message_id
        )
    except chat_schema.MessageCancelledException as e:
        logger.warning(f"Message was cancelled before work could be initiated: {e.message_id=}")
    except chat_schema.MessageTimeoutException as e:
        logger.warning(f"Message timed out before work could be initiated: {e.message.id=}")
        await handle_timeout(message=e.message)
    finally:
        futures.ensure_listening_for_work_requests()


async def _handle_worker_response(
    worker_response: inference.WorkerResponse,
    context: HandleWorkerContext,
    futures: FuturesManager,
    session: SessionManager,
):
    try:
        match worker_response.response_type:
            case "pong":
                worker_response = cast(inference.PongResponse, worker_response)
                await session.update(worker_response.metrics)
            case "token":
                worker_response = cast(inference.TokenResponse, worker_response)
                await handle_token_response(
                    work_request_map=context.work_request_map,
                    response=worker_response,
                )
            case "generated_text":
                worker_response = cast(inference.GeneratedTextResponse, worker_response)
                await handle_generated_text_response(
                    work_request_map=context.work_request_map,
                    response=worker_response,
                )
                await session.update(worker_response.metrics)
            case "error":
                worker_response = cast(inference.ErrorResponse, worker_response)
                await handle_error_response(
                    work_request_map=context.work_request_map,
                    response=worker_response,
                )
                await session.update(worker_response.metrics)
            case "general_error":
                worker_response = cast(inference.GeneralErrorResponse, worker_response)
                await handle_general_error_response(
                    response=worker_response,
                )
                await session.update(worker_response.metrics)
            case "safe_prompt":
                logger.info("Received safe prompt response")
                worker_response = cast(inference.SafePromptResponse, worker_response)
                await handle_safe_prompt_response(
                    response=worker_response,
                    work_request_map=context.work_request_map,
                )
            case "plugin_intermediate":
                worker_response = cast(inference.PluginIntermediateResponse, worker_response)
                await handle_plugin_intermediate_response(
                    work_request_map=context.work_request_map,
                    response=worker_response,
                )
            case _:
                raise RuntimeError(f"Unknown response type: {worker_response.response_type}")
    finally:
        if len(futures._futures) == 0:
            futures.ensure_listening_for_work_requests()
        futures.ensure_listening_to_worker_responses()


async def _reset_or_abort_open_work_requests(context: HandleWorkerContext):
    logger.info(f"Handling {context.num_requests_in_progress} work requests outstanding")
    for container in context.work_request_map.values():
        try:
            message_id = container.message_id
            if container.num_responses == 0:
                logger.warning(f"Marking {message_id=} as pending since no work was done.")
                async with deps.manual_chat_repository() as cr:
                    await cr.reset_work(message_id)
                await context.work_queue.enqueue(message_id, enforce_max_size=False)
            else:
                logger.warning(f"Aborting {message_id=}")
                await abort_message(message_id=message_id, error="Aborted due to worker error.")
        except Exception as e:
            logger.exception(f"Error while trying to reset work for {message_id=}: {str(e)}")


@router.websocket("/work")
async def handle_worker(
    websocket: fastapi.WebSocket,
    api_key: str = worker_utils.api_key_header,
    protocol_version: str = worker_utils.protocol_version_header,
):
    await websocket.accept()

    try:
        context = await HandleWorkerContext.build(websocket, api_key, protocol_version)
        futures = FuturesManager(context)
        session = SessionManager(context)
        await session.init()
        futures.ensure_listening_for_work_requests()
        futures.ensure_listening_to_worker_responses()

        logger.info(f"handle_worker: {context.worker_id=} started")
        while True:
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                raise WorkerDisconnectException("Worker disconnected")

            results = await futures.wait_for_event_or_timeout()
            for type_, result in results:
                if type_ == FutureType.WORK_REQUEST:
                    _, message_id = result
                    await _handle_work_request(message_id, context, futures)
                elif type_ == FutureType.WORKER_RESPONSE:
                    worker_response = cast(inference.WorkerResponse, result)
                    await _handle_worker_response(worker_response, context, futures, session)
                else:
                    raise ValueError(f"Unexpected future type: {type_}")

            if len(results) == 0:
                await worker_utils.send_worker_request(websocket, inference.PingRequest())

    except Exception as e:
        logger.exception(f"Error while handling worker {context.worker_id}: {str(e)}")
        await _reset_or_abort_open_work_requests(context)
    finally:
        logger.info(f"Worker {context.worker_id} disconnected")
        await session.close()
        futures.cancel_all()
        await context.close()


@router.get("/sessions")
async def list_worker_sessions() -> list[worker_utils.WorkerSession]:
    redis_client = deps.redis_client
    try:
        worker_sessions = []
        async for key in redis_client.scan_iter("worker_session:*"):
            worker_session_json = await redis_client.get(key)
            worker_session = worker_utils.WorkerSession.parse_raw(worker_session_json)
            worker_sessions.append(worker_session)
    except Exception as e:
        logger.exception(f"Error while listing worker sessions: {str(e)}")
        raise
    return worker_sessions


@router.on_event("startup")
async def clear_worker_sessions():
    redis_client = deps.redis_client
    try:
        logger.warning("Clearing worker sessions")
        async for key in redis_client.scan_iter("worker_session:*"):
            await redis_client.getdel(key)
        logger.warning("Successfully cleared worker sessions")
    except Exception as e:
        logger.exception(f"Error while clearing worker sessions: {str(e)}")
        raise


async def initiate_work_for_message(
    *,
    websocket: fastapi.WebSocket,
    work_queue: queueing.RedisQueue,
    message_id: str,
    worker_id: str,
    worker_config: inference.WorkerConfig,
) -> inference.WorkRequest:
    async with deps.manual_create_session() as session:
        cr = chat_repository.ChatRepository(session=session)

        message = await cr.start_work(
            message_id=message_id,
            worker_id=worker_id,
            worker_config=worker_config,
        )
        work_request = await worker_utils.build_work_request(session, message.id)

    logger.info(f"Created {work_request=} with {len(work_request.thread.messages)=}")
    try:
        await worker_utils.send_worker_request(websocket, work_request)
    except Exception as e:
        logger.exception(f"Error while sending work request to worker: {str(e)}")
        async with deps.manual_create_session() as session:
            await cr.reset_work(message_id)
        await work_queue.enqueue(message_id, enforce_max_size=False)
        raise

    return work_request


async def handle_token_response(
    response: inference.TokenResponse,
    work_request_map: WorkRequestContainerMap,
):
    work_response_container = get_work_request_container(work_request_map, response.request_id)
    message_queue = queueing.message_queue(
        deps.redis_client,
        message_id=work_response_container.message_id,
    )
    await message_queue.enqueue(response.json())
    work_response_container.num_responses += 1


async def handle_plugin_intermediate_response(
    response: inference.PluginIntermediateResponse,
    work_request_map: WorkRequestContainerMap,
):
    work_response_container = get_work_request_container(work_request_map, response.request_id)
    message_queue = queueing.message_queue(
        deps.redis_client,
        message_id=work_response_container.message_id,
    )
    await message_queue.enqueue(response.json())
    work_response_container.num_responses += 1


async def handle_generated_text_response(
    response: inference.GeneratedTextResponse,
    work_request_map: WorkRequestContainerMap,
):
    try:
        work_response_container = get_work_request_container(work_request_map, response.request_id)
        message_id = work_response_container.message_id
        async with deps.manual_create_session() as session:
            cr = chat_repository.ChatRepository(session=session)
            message = await cr.complete_work(
                message_id=message_id,
                content=response.text,
                used_plugin=response.used_plugin,
            )
            logger.info(f"Completed work for {message_id=}")
        message_packet = inference.InternalFinishedMessageResponse(
            message=message.to_read(),
        )
        message_queue = queueing.message_queue(
            deps.redis_client,
            message_id=message_id,
        )
        await message_queue.enqueue(message_packet.json())
    finally:
        del work_request_map[response.request_id]


async def abort_message(message_id: str, error: str):
    async with deps.manual_chat_repository() as cr:
        message = await cr.abort_work(message_id, reason=error)
    response = inference.InternalErrorResponse(error=error, message=message.to_read())
    message_queue = queueing.message_queue(
        deps.redis_client,
        message_id=message_id,
    )
    await message_queue.enqueue(response.json())


async def handle_error_response(
    response: inference.ErrorResponse,
    work_request_map: WorkRequestContainerMap,
):
    logger.warning(f"Got error {response=}")
    try:
        work_response_container = get_work_request_container(work_request_map, response.request_id)
        message_id = work_response_container.message_id
        await abort_message(message_id, response.error)
    finally:
        del work_request_map[response.request_id]


async def handle_general_error_response(
    response: inference.GeneralErrorResponse,
):
    logger.warning(f"Got general error {response=}")


async def handle_safe_prompt_response(
    response: inference.SafePromptResponse,
    work_request_map: WorkRequestContainerMap,
):
    """
    Handle the case where the worker informs the server that the safety model has intervened and modified the user prompt to be safe.
    """
    work_response_container = get_work_request_container(work_request_map, response.request_id)
    message_id = work_response_container.message_id

    async with deps.manual_create_session() as session:
        cr = chat_repository.ChatRepository(session=session)
        message = await cr.get_assistant_message_by_id(message_id)
        prompt = await cr.get_prompter_message_by_id(message.parent_id)
        prompt.safe_content = response.safe_prompt
        prompt.safety_level = response.safety_parameters.level
        prompt.safety_label = response.safety_label
        prompt.safety_rots = response.safety_rots
        await session.commit()


async def handle_timeout(message: inference.MessageRead):
    response = inference.InternalErrorResponse(
        error="Timeout",
        message=message,
    )
    message_queue = queueing.message_queue(
        deps.redis_client,
        message_id=message.id,
    )
    await message_queue.enqueue(response.json())
