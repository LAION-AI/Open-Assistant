import random
from typing import Any, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.api.v1.utils import prepare_conversation
from oasst_backend.prompt_repository import PromptRepository, TaskRepository
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


def generate_task(
    request: protocol_schema.TaskRequest, pr: PromptRepository
) -> Tuple[protocol_schema.Task, Optional[UUID], Optional[UUID]]:
    message_tree_id = None
    parent_message_id = None

    match request.type:
        case protocol_schema.TaskRequestType.random:
            logger.info("Frontend requested a random task.")
            disabled_tasks = (
                protocol_schema.TaskRequestType.random,
                protocol_schema.TaskRequestType.summarize_story,
                protocol_schema.TaskRequestType.rate_summary,
            )
            candidate_tasks = set(protocol_schema.TaskRequestType).difference(disabled_tasks)
            request.type = random.choice(tuple(candidate_tasks)).value
            return generate_task(request, pr)

        # AKo: Summary tasks are currently disabled/supported, we focus on the conversation tasks.

        # case protocol_schema.TaskRequestType.summarize_story:
        #     logger.info("Generating a SummarizeStoryTask.")
        #     task = protocol_schema.SummarizeStoryTask(
        #         story="This is a story. A very long story. So long, it needs to be summarized.",
        #     )
        # case protocol_schema.TaskRequestType.rate_summary:
        #     logger.info("Generating a RateSummaryTask.")
        #     task = protocol_schema.RateSummaryTask(
        #         full_text="This is a story. A very long story. So long, it needs to be summarized.",
        #         summary="This is a summary.",
        #         scale=protocol_schema.RatingScale(min=1, max=5),
        #     )

        case protocol_schema.TaskRequestType.initial_prompt:
            logger.info("Generating an InitialPromptTask.")
            task = protocol_schema.InitialPromptTask(
                hint="Ask the assistant about a current event."  # this is optional
            )
        case protocol_schema.TaskRequestType.prompter_reply:
            logger.info("Generating a PrompterReplyTask.")
            messages = pr.fetch_random_conversation("assistant")
            task_messages = [
                protocol_schema.ConversationMessage(
                    text=msg.text,
                    is_assistant=(msg.role == "assistant"),
                    message_id=msg.id,
                    front_end_id=msg.frontend_message_id,
                )
                for msg in messages
            ]

            task = protocol_schema.PrompterReplyTask(conversation=protocol_schema.Conversation(messages=task_messages))
            message_tree_id = messages[-1].message_tree_id
            parent_message_id = messages[-1].id
        case protocol_schema.TaskRequestType.assistant_reply:
            logger.info("Generating a AssistantReplyTask.")
            messages = pr.fetch_random_conversation("prompter")
            task_messages = [
                protocol_schema.ConversationMessage(
                    text=msg.text,
                    is_assistant=(msg.role == "assistant"),
                    message_id=msg.id,
                    front_end_id=msg.frontend_message_id,
                )
                for msg in messages
            ]

            task = protocol_schema.AssistantReplyTask(conversation=protocol_schema.Conversation(messages=task_messages))
            message_tree_id = messages[-1].message_tree_id
            parent_message_id = messages[-1].id
        case protocol_schema.TaskRequestType.rank_initial_prompts:
            logger.info("Generating a RankInitialPromptsTask.")

            messages = pr.fetch_random_initial_prompts()
            task = protocol_schema.RankInitialPromptsTask(prompts=[msg.text for msg in messages])
        case protocol_schema.TaskRequestType.rank_prompter_replies:
            logger.info("Generating a RankPrompterRepliesTask.")
            conversation, replies = pr.fetch_multiple_random_replies(message_role="assistant")

            task_messages = [
                protocol_schema.ConversationMessage(
                    text=p.text,
                    is_assistant=(p.role == "assistant"),
                    message_id=p.id,
                    front_end_id=p.frontend_message_id,
                )
                for p in conversation
            ]
            replies = [p.text for p in replies]
            task = protocol_schema.RankPrompterRepliesTask(
                conversation=protocol_schema.Conversation(
                    messages=task_messages,
                ),
                replies=replies,
            )

        case protocol_schema.TaskRequestType.rank_assistant_replies:
            logger.info("Generating a RankAssistantRepliesTask.")
            conversation, replies = pr.fetch_multiple_random_replies(message_role="prompter")

            task_messages = [
                protocol_schema.ConversationMessage(
                    text=p.text,
                    is_assistant=(p.role == "assistant"),
                    message_id=p.id,
                    front_end_id=p.frontend_message_id,
                )
                for p in conversation
            ]
            replies = [p.text for p in replies]
            task = protocol_schema.RankAssistantRepliesTask(
                conversation=prepare_conversation(conversation),
                replies=replies,
            )

        case protocol_schema.TaskRequestType.label_initial_prompt:
            logger.info("Generating a LabelInitialPromptTask.")
            message = pr.fetch_random_initial_prompts(1)[0]
            task = protocol_schema.LabelInitialPromptTask(
                message_id=message.id,
                prompt=message.text,
                valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
            )

        case protocol_schema.TaskRequestType.label_prompter_reply:
            logger.info("Generating a LabelPrompterReplyTask.")
            conversation, messages = pr.fetch_multiple_random_replies(max_size=1, message_role="assistant")
            message = messages[0]
            task = protocol_schema.LabelPrompterReplyTask(
                message_id=message.id,
                conversation=prepare_conversation(conversation),
                reply=message.text,
                valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
            )

        case protocol_schema.TaskRequestType.label_assistant_reply:
            logger.info("Generating a LabelAssistantReplyTask.")
            conversation, messages = pr.fetch_multiple_random_replies(max_size=1, message_role="prompter")
            message = messages[0]
            task = protocol_schema.LabelAssistantReplyTask(
                message_id=message.id,
                conversation=prepare_conversation(conversation),
                reply=message.text,
                valid_labels=list(map(lambda x: x.value, protocol_schema.TextLabel)),
            )

        case _:
            raise OasstError("Invalid request type", OasstErrorCode.TASK_INVALID_REQUEST_TYPE)

    logger.info(f"Generated {task=}.")

    return task, message_tree_id, parent_message_id


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
        task, message_tree_id, parent_message_id = generate_task(request, pr)
        pr.task_repository.store_task(task, message_tree_id, parent_message_id, request.collective)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to generate task..")
        raise OasstError("Failed to generate task.", OasstErrorCode.TASK_GENERATION_FAILED)
    return task


@router.post("/{task_id}/ack", response_model=None, status_code=HTTP_204_NO_CONTENT)
def tasks_acknowledge(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    task_id: UUID,
    ack_request: protocol_schema.TaskAck,
) -> None:
    """
    The frontend acknowledges a task.
    """

    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client)

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
    task_id: UUID,
    nack_request: protocol_schema.TaskNAck,
) -> None:
    """
    The frontend reports failure to implement a task.
    """

    try:
        logger.info(f"Frontend reports failure to implement task {task_id=}, {nack_request=}.")
        api_client = deps.api_auth(api_key, db)
        pr = PromptRepository(db, api_client)
        pr.task_repository.acknowledge_task_failure(task_id)
    except (KeyError, RuntimeError):
        logger.exception("Failed to not acknowledge task.")
        raise OasstError("Failed to not acknowledge task.", OasstErrorCode.TASK_NACK_FAILED)


@router.post("/interaction", response_model=protocol_schema.TaskDone)
def tasks_interaction(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.AnyInteraction,
) -> Any:
    """
    The frontend reports an interaction.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, client_user=interaction.user)

        match type(interaction):
            case protocol_schema.TextReplyToMessage:
                logger.info(
                    f"Frontend reports text reply to {interaction.message_id=} with {interaction.text=} by {interaction.user=}."
                )

                # here we store the text reply in the database
                pr.store_text_reply(
                    text=interaction.text,
                    frontend_message_id=interaction.message_id,
                    user_frontend_message_id=interaction.user_message_id,
                )

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRating:
                logger.info(
                    f"Frontend reports rating of {interaction.message_id=} with {interaction.rating=} by {interaction.user=}."
                )

                # here we store the rating in the database
                pr.store_rating(interaction)

                return protocol_schema.TaskDone()
            case protocol_schema.MessageRanking:
                logger.info(
                    f"Frontend reports ranking of {interaction.message_id=} with {interaction.ranking=} by {interaction.user=}."
                )

                # TODO: check if the ranking is valid
                pr.store_ranking(interaction)
                # here we would store the ranking in the database
                return protocol_schema.TaskDone()
            case protocol_schema.TextLabels:
                logger.info(
                    f"Frontend reports labels of {interaction.message_id=} with {interaction.labels=} by {interaction.user=}."
                )
                # Labels are implicitly validated when converting str -> TextLabel
                # So no need for explicit validation here
                pr.store_text_labels(interaction)
                return protocol_schema.TaskDone()
            case _:
                raise OasstError("Invalid response type.", OasstErrorCode.TASK_INVALID_RESPONSE_TYPE)
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
