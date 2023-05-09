import asyncio
import base64

import fastapi
import pydantic
from fastapi import Depends, Query
from loguru import logger
from oasst_inference_server import auth, chat_utils, deps, models, queueing
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.settings import settings
from oasst_inference_server.user_chat_repository import UserChatRepository
from oasst_shared.schemas import inference
from sse_starlette.sse import EventSourceResponse

router = fastapi.APIRouter(
    prefix="/chats",
    tags=["chats"],
)


@router.get("")
async def list_chats(
    include_hidden: bool = False,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
    limit: int | None = Query(10, gt=0, le=100),
    after: str | None = None,
    before: str | None = None,
) -> chat_schema.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")

    def encode_cursor(chat: models.DbChat):
        return base64.b64encode(chat.id.encode()).decode()

    def decode_cursor(cursor: str | None):
        if cursor is None:
            return None
        return base64.b64decode(cursor.encode()).decode()

    chats = await ucr.get_chats(
        include_hidden=include_hidden, limit=limit + 1, after=decode_cursor(after), before=decode_cursor(before)
    )

    num_rows = len(chats)
    chats = chats if num_rows <= limit else chats[:-1]  # remove extra item
    chats = chats if before is None else chats[::-1]  # reverse if query in backward direction

    def get_cursors():
        prev, next = None, None
        if num_rows > 0:
            if (num_rows > limit and before) or after:
                prev = encode_cursor(chats[0])
            if num_rows > limit or before:
                next = encode_cursor(chats[-1])
        else:
            if after:
                prev = after
            if before:
                next = before
        return prev, next

    prev, next = get_cursors()

    chats_list = [chat.to_list_read() for chat in chats]
    return chat_schema.ListChatsResponse(chats=chats_list, next=next, prev=prev)


@router.post("")
async def create_chat(
    request: chat_schema.CreateChatRequest,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ChatListRead:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request=}")
    chat = await ucr.create_chat()
    return chat.to_list_read()


@router.get("/{chat_id}")
async def get_chat(
    chat_id: str,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ChatRead:
    """Allows a client to get the current state of a chat."""
    chat = await ucr.get_chat_by_id(chat_id)
    return chat.to_read()


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
):
    await ucr.delete_chat(chat_id)
    return fastapi.Response(status_code=200)


@router.post("/{chat_id}/prompter_message")
async def create_prompter_message(
    chat_id: str,
    request: chat_schema.CreatePrompterMessageRequest,
    user_id: str = Depends(auth.get_current_user_id),
) -> inference.MessageRead:
    """Adds a prompter message to a chat."""

    try:
        ucr: UserChatRepository
        async with deps.manual_user_chat_repository(user_id) as ucr:
            prompter_message = await ucr.add_prompter_message(
                chat_id=chat_id, parent_id=request.parent_id, content=request.content
            )
        return prompter_message.to_read()
    except fastapi.HTTPException:
        raise
    except Exception:
        logger.exception("Error adding prompter message")
        return fastapi.Response(status_code=500)


@router.post("/{chat_id}/assistant_message")
async def create_assistant_message(
    chat_id: str,
    request: chat_schema.CreateAssistantMessageRequest,
    user_id: str = Depends(auth.get_current_user_id),
) -> inference.MessageRead:
    """Allows the client to stream the results of a request."""

    try:
        model_config = chat_utils.get_model_config(request.model_config_name)
    except ValueError as e:
        logger.warning(str(e))
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    try:
        ucr: UserChatRepository
        async with deps.manual_user_chat_repository(user_id) as ucr:
            work_parameters = inference.WorkParameters(
                model_config=model_config,
                sampling_parameters=request.sampling_parameters,
                plugins=request.plugins,
            )
            assistant_message = await ucr.initiate_assistant_message(
                parent_id=request.parent_id,
                work_parameters=work_parameters,
                worker_compat_hash=model_config.compat_hash,
            )
        queue = queueing.work_queue(deps.redis_client, model_config.compat_hash)
        logger.debug(f"Adding {assistant_message.id=} to {queue.queue_id} for {chat_id}")
        await queue.enqueue(assistant_message.id)
        logger.debug(f"Added {assistant_message.id=} to {queue.queue_id} for {chat_id}")
        return assistant_message.to_read()
    except queueing.QueueFullException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The server is currently busy. Please try again later.",
        )
    except fastapi.HTTPException:
        raise
    except Exception:
        logger.exception("Error adding prompter message")
        return fastapi.Response(status_code=500)


@router.get("/{chat_id}/messages/{message_id}")
async def get_message(
    chat_id: str,
    message_id: str,
    user_id: str = Depends(auth.get_current_user_id),
) -> inference.MessageRead:
    ucr: UserChatRepository
    async with deps.manual_user_chat_repository(user_id) as ucr:
        message: models.DbMessage = await ucr.get_message_by_id(chat_id=chat_id, message_id=message_id)
    return message.to_read()


@router.get("/{chat_id}/messages/{message_id}/events")
async def message_events(
    chat_id: str,
    message_id: str,
    fastapi_request: fastapi.Request,
    user_id: str = Depends(auth.get_current_user_id),
) -> EventSourceResponse:
    ucr: UserChatRepository
    async with deps.manual_user_chat_repository(user_id) as ucr:
        message: models.DbMessage = await ucr.get_message_by_id(chat_id=chat_id, message_id=message_id)
    if message.role != "assistant":
        raise fastapi.HTTPException(status_code=400, detail="Only assistant messages can be streamed.")

    if message.has_finished:
        raise fastapi.HTTPException(status_code=204, detail=message.state)

    async def event_generator(chat_id: str, message_id: str, worker_compat_hash: str | None):
        redis_client = deps.make_redis_client()
        message_queue = queueing.message_queue(redis_client, message_id=message_id)
        work_queue = (
            queueing.work_queue(redis_client, worker_compat_hash=worker_compat_hash)
            if worker_compat_hash is not None
            else None
        )
        has_started = False
        try:
            while True:
                item = await message_queue.dequeue(timeout=settings.pending_event_interval)
                if item is None:
                    if not has_started:
                        if work_queue is None:
                            qpos, qlen = 0, 1
                        else:
                            # TODO: make more efficient, e.g. pipeline
                            [qdeq, qenq, mpos] = await asyncio.gather(
                                work_queue.get_deq_counter(),
                                work_queue.get_enq_counter(),
                                queueing.get_pos_value(redis_client, message_id),
                            )
                            qpos = max(mpos - qdeq, 0)
                            qlen = max(qenq - qdeq, qpos)
                        yield {
                            "data": chat_schema.PendingResponseEvent(
                                queue_position=qpos,
                                queue_size=qlen,
                            ).json()
                        }
                    continue
                has_started = True

                _, response_packet_str = item
                response_packet = pydantic.parse_raw_as(inference.WorkerResponse, response_packet_str)

                if response_packet.response_type in ("error", "generated_text"):
                    logger.warning(
                        f"Received {response_packet.response_type=} response for {chat_id}. This should not happen."
                    )
                    break

                if response_packet.response_type == "safe_prompt":
                    logger.info(f"Received safety intervention for {chat_id}")
                    yield {
                        "data": chat_schema.SafePromptResponseEvent(
                            safe_prompt=response_packet.safe_prompt,
                        ).json(),
                    }

                if response_packet.response_type == "internal_error":
                    yield {
                        "data": chat_schema.ErrorResponseEvent(
                            error=response_packet.error, message=response_packet.message
                        ).json(),
                    }
                    break

                if response_packet.response_type == "internal_finished_message":
                    yield {
                        "data": chat_schema.MessageResponseEvent(message=response_packet.message).json(),
                    }
                    break

                yield {
                    "data": chat_schema.TokenResponseEvent(text=response_packet.text).json(),
                }

            if await fastapi_request.is_disconnected():
                logger.warning(f"Client disconnected while streaming {chat_id}")

            logger.info(f"Finished streaming {chat_id}")
        except Exception:
            logger.exception(f"Error streaming {chat_id}")
            raise
        finally:
            await redis_client.close()

    return EventSourceResponse(
        event_generator(chat_id=chat_id, message_id=message_id, worker_compat_hash=message.worker_compat_hash)
    )


@router.post("/{chat_id}/messages/{message_id}/votes")
async def handle_create_vote(
    message_id: str,
    vote_request: chat_schema.VoteRequest,
    ucr: deps.UserChatRepository = fastapi.Depends(deps.create_user_chat_repository),
) -> fastapi.Response:
    """Allows the client to vote on a message."""
    try:
        await ucr.update_score(message_id=message_id, score=vote_request.score)
        return fastapi.Response(status_code=200)
    except Exception:
        logger.exception("Error adding vote")
        return fastapi.Response(status_code=500)


@router.post("/{chat_id}/messages/{message_id}/reports")
async def handle_create_report(
    message_id: str,
    report_request: chat_schema.ReportRequest,
    ucr: deps.UserChatRepository = fastapi.Depends(deps.create_user_chat_repository),
) -> fastapi.Response:
    """Allows the client to report a message."""
    try:
        await ucr.add_report(
            message_id=message_id, report_type=report_request.report_type, reason=report_request.reason
        )
        return fastapi.Response(status_code=200)
    except Exception:
        logger.exception("Error adding report")
        return fastapi.Response(status_code=500)


@router.put("/{chat_id}")
async def handle_update_chat(
    chat_id: str,
    request: chat_schema.ChatUpdateRequest,
    ucr: deps.UserChatRepository = fastapi.Depends(deps.create_user_chat_repository),
) -> fastapi.Response:
    """Allows the client to update a chat."""
    try:
        await ucr.update_chat(
            chat_id=chat_id,
            title=request.title,
            hidden=request.hidden,
            allow_data_use=request.allow_data_use,
        )
    except Exception:
        logger.exception("Error when updating chat")
        return fastapi.Response(status_code=500)
