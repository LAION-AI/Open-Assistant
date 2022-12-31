# -*- coding: utf-8 -*-
"""API Client for interacting with the OASST backend."""
import enum
import typing as t
from typing import Optional, Type
from uuid import UUID

import aiohttp
from loguru import logger
from oasst_shared.schemas import protocol as protocol_schema


# TODO: Move to `protocol`?
class TaskType(str, enum.Enum):
    """Task types."""

    summarize_story = "summarize_story"
    rate_summary = "rate_summary"
    initial_prompt = "initial_prompt"
    prompter_reply = "prompter_reply"
    assistant_reply = "assistant_reply"
    rank_initial_prompts = "rank_initial_prompts"
    rank_prompter_replies = "rank_prompter_replies"
    rank_assistant_replies = "rank_assistant_replies"
    done = "task_done"


class OasstApiClient:
    """API Client for interacting with the OASST backend."""

    def __init__(self, backend_url: str, api_key: str):
        """Create a new OasstApiClient.

        Args:
        ----
            backend_url (str): The base backend URL.
            api_key (str): The API key to use for authentication.
        """
        logger.debug("Opening OasstApiClient session")
        self.session = aiohttp.ClientSession()
        self.backend_url = backend_url
        self.api_key = api_key

        self.task_models_map: dict[TaskType, Type[protocol_schema.Task]] = {
            TaskType.summarize_story: protocol_schema.SummarizeStoryTask,
            TaskType.rate_summary: protocol_schema.RateSummaryTask,
            TaskType.initial_prompt: protocol_schema.InitialPromptTask,
            TaskType.prompter_reply: protocol_schema.PrompterReplyTask,
            TaskType.assistant_reply: protocol_schema.AssistantReplyTask,
            TaskType.rank_initial_prompts: protocol_schema.RankInitialPromptsTask,
            TaskType.rank_prompter_replies: protocol_schema.RankPrompterRepliesTask,
            TaskType.rank_assistant_replies: protocol_schema.RankAssistantRepliesTask,
            TaskType.done: protocol_schema.TaskDone,
        }

    async def post(self, path: str, data: dict[str, t.Any]) -> dict[str, t.Any]:
        """Make a POST request to the backend."""
        logger.debug(f"POST {self.backend_url}{path} DATA: {data}")
        response = await self.session.post(f"{self.backend_url}{path}", json=data, headers={"X-API-Key": self.api_key})
        response.raise_for_status()
        return await response.json()

    def _parse_task(self, data: dict[str, t.Any]) -> protocol_schema.Task:
        task_type = TaskType(data.get("type"))

        model = self.task_models_map.get(task_type)
        if not model:
            logger.error(f"Unsupported task type: {task_type}")
            raise ValueError(f"Unsupported task type: {task_type}")
        return self.task_models_map[task_type].parse_obj(data)  # type: ignore

    async def fetch_task(
        self,
        task_type: protocol_schema.TaskRequestType,
        user: Optional[protocol_schema.User] = None,
        collective: bool = False,
    ) -> protocol_schema.Task:
        """Fetch a task from the backend."""
        logger.debug(f"Fetching task {task_type} for user {user}")
        req = protocol_schema.TaskRequest(type=task_type.value, user=user, collective=collective)
        resp = await self.post("/api/v1/tasks/", data=req.dict())
        logger.debug(f"RESP {resp}")
        return self._parse_task(resp)

    async def fetch_random_task(
        self, user: Optional[protocol_schema.User] = None, collective: bool = False
    ) -> protocol_schema.Task:
        """Fetch a random task from the backend."""
        logger.debug(f"Fetching random for user {user}")
        return await self.fetch_task(protocol_schema.TaskRequestType.random, user, collective)

    async def ack_task(self, task_id: str | UUID, message_id: str):
        """Send an ACK for a task to the backend."""
        logger.debug(f"ACK task {task_id} with post {message_id}")
        req = protocol_schema.TaskAck(message_id=message_id)
        return await self.post(f"/api/v1/tasks/{task_id}/ack", data=req.dict())

    async def nack_task(self, task_id: str | UUID, reason: str):
        """Send a NACK for a task to the backend."""
        logger.debug(f"NACK task {task_id} with reason {reason}")
        req = protocol_schema.TaskNAck(reason=reason)
        return await self.post(f"/api/v1/tasks/{task_id}/nack", data=req.dict())

    async def post_interaction(self, interaction: protocol_schema.Interaction) -> protocol_schema.Task:
        """Send a completed task to the backend."""
        logger.debug(f"Interaction: {interaction}")
        resp = await self.post("/api/v1/tasks/interaction", data=interaction.dict())

        return self._parse_task(resp)

    async def close(self):
        logger.debug("Closing OasstApiClient session")
        await self.session.close()
