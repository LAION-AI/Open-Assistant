import fastapi
from fastapi import Depends
from loguru import logger
from oasst_inference_server import auth, deps, models, queueing
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.user_chat_repository import UserChatRepository
from oasst_shared.schemas import inference
from sse_starlette.sse import EventSourceResponse

router = fastapi.APIRouter(
    prefix="/chats",
    tags=["chats"],
)


@router.get("/")
async def list_chats(
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> chat_schema.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")
    chats = await ucr.get_chats()
    chats_list = [chat.to_list_read() for chat in chats]
    return chat_schema.ListChatsResponse(chats=chats_list)


@router.post("/")
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


@router.post("/{chat_id}/messages")
async def create_message(
    chat_id: str,
    request: chat_schema.CreateMessageRequest,
    user_id: str = Depends(auth.get_current_user_id),
) -> chat_schema.CreateMessageResponse:
    """Allows the client to stream the results of a request."""

    async with deps.manual_user_chat_repository(user_id) as ucr:
        try:
            prompter_message = await ucr.add_prompter_message(
                chat_id=chat_id, parent_id=request.parent_id, content=request.content
            )
            assistant_message = await ucr.initiate_assistant_message(
                parent_id=prompter_message.id,
                work_parameters=request.work_parameters,
            )
            queue = queueing.work_queue(deps.redis_client, request.worker_compat_hash)
            logger.debug(f"Adding {assistant_message.id=} to {queue.queue_id} for {chat_id}")
            await queue.enqueue(assistant_message.id)
            logger.debug(f"Added {assistant_message.id=} to {queue.queue_id} for {chat_id}")
            prompter_message_read = prompter_message.to_read()
            assistant_message_read = assistant_message.to_read()
        except Exception:
            logger.exception("Error adding prompter message")
            return fastapi.Response(status_code=500)

    return chat_schema.CreateMessageResponse(
        prompter_message=prompter_message_read,
        assistant_message=assistant_message_read,
    )


@router.get("/{chat_id}/messages/{message_id}/events")
async def message_events(
    chat_id: str,
    message_id: str,
    fastapi_request: fastapi.Request,
    ucr: UserChatRepository = Depends(deps.create_user_chat_repository),
) -> EventSourceResponse:
    message: models.DbMessage = await ucr.get_message_by_id(chat_id=chat_id, message_id=message_id)
    if message.role != "assistant":
        raise fastapi.HTTPException(status_code=400, detail="Only assistant messages can be streamed.")

    if message.state not in (inference.MessageState.in_progress, inference.MessageState.pending):
        raise fastapi.HTTPException(status_code=204, detail="Message is not in progress.")

    async def event_generator(chat_id: str, message_id: str):
        queue = queueing.message_queue(deps.redis_client, message_id=message_id)
        try:
            while True:
                item = await queue.dequeue()
                if item is None:
                    continue

                _, response_packet_str = item
                response_packet = inference.WorkResponsePacket.parse_raw(response_packet_str)
                if response_packet.error is not None:
                    yield {
                        "data": chat_schema.TokenResponseEvent(error=response_packet.error).json(),
                    }
                    break

                if response_packet.is_end:
                    break

                if await fastapi_request.is_disconnected():
                    continue

                yield {
                    "data": chat_schema.TokenResponseEvent(token=response_packet.token).json(),
                }

            if await fastapi_request.is_disconnected():
                logger.warning(f"Client disconnected while streaming {chat_id}")

            logger.info(f"Finished streaming {chat_id}")
        except Exception:
            logger.exception(f"Error streaming {chat_id}")
            raise

    return EventSourceResponse(event_generator(chat_id=chat_id, message_id=message_id))


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
