import fastapi
from fastapi import Depends
from loguru import logger
from oasst_inference_server import auth, deps, queueing
from oasst_inference_server.schemas import chat as chat_schema
from oasst_shared.schemas import inference
from sse_starlette.sse import EventSourceResponse


async def handle_create_message(
    chat_id: str,
    message_request: chat_schema.MessageRequest,
    fastapi_request: fastapi.Request,
    user_id: str = Depends(auth.get_current_user_id),
) -> EventSourceResponse:
    """Allows the client to stream the results of a request."""

    with deps.manual_user_chat_repository(user_id) as ucr:
        try:
            prompter_message = ucr.add_prompter_message(
                chat_id=chat_id, parent_id=message_request.parent_id, content=message_request.content
            )
            assistant_message = ucr.initiate_assistant_message(
                parent_id=prompter_message.id,
                work_parameters=message_request.work_parameters,
            )
            queue = queueing.work_queue(deps.redis_client, message_request.worker_compat_hash)
            logger.debug(f"Adding {assistant_message.id=} to {queue.queue_id} for {chat_id}")
            await queue.enqueue(assistant_message.id)
            logger.debug(f"Added {assistant_message.id=} to {queue.queue_id} for {chat_id}")
            prompter_message_read = prompter_message.to_read()
            assistant_message_read = assistant_message.to_read()
        except Exception:
            logger.exception("Error adding prompter message")
            return fastapi.Response(status_code=500)

    async def event_generator(prompter_message: inference.MessageRead, assistant_message: inference.MessageRead):
        queue = queueing.message_queue(deps.redis_client, assistant_message.id)
        try:
            yield {
                "data": chat_schema.MessageResponseEvent(
                    prompter_message=prompter_message,
                    assistant_message=assistant_message,
                ).json(),
            }
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

    return EventSourceResponse(
        event_generator(
            prompter_message=prompter_message_read,
            assistant_message=assistant_message_read,
        )
    )


async def handle_create_vote(
    message_id: str,
    vote_request: chat_schema.VoteRequest,
    ucr: deps.UserChatRepository = fastapi.Depends(deps.create_user_chat_repository),
) -> fastapi.Response:
    """Allows the client to vote on a message."""
    try:
        ucr.add_vote(message_id=message_id, score=vote_request.score)
        return fastapi.Response(status_code=200)
    except Exception:
        logger.exception("Error adding vote")
        return fastapi.Response(status_code=500)


async def handle_create_report(
    message_id: str,
    report_request: chat_schema.ReportRequest,
    ucr: deps.UserChatRepository = fastapi.Depends(deps.create_user_chat_repository),
) -> fastapi.Response:
    """Allows the client to report a message."""
    try:
        ucr.add_report(message_id=message_id, report_type=report_request.report_type, reason=report_request.reason)
        return fastapi.Response(status_code=200)
    except Exception:
        logger.exception("Error adding report")
        return fastapi.Response(status_code=500)
