# -*- coding: utf-8 -*-
import enum
from typing import Optional, Type

import requests
from oasst_shared.schemas import protocol as protocol_schema


class TaskType(str, enum.Enum):
    summarize_story = "summarize_story"
    rate_summary = "rate_summary"
    initial_prompt = "initial_prompt"
    user_reply = "user_reply"
    assistant_reply = "assistant_reply"
    rank_initial_prompts = "rank_initial_prompts"
    rank_user_replies = "rank_user_replies"
    rank_assistant_replies = "rank_assistant_replies"
    done = "task_done"


class ApiClient:
    def __init__(self, backend_url: str, api_key: str):
        self.backend_url = backend_url
        self.api_key = api_key

        task_models_map: dict[str, Type[protocol_schema.Task]] = {
            TaskType.summarize_story: protocol_schema.SummarizeStoryTask,
            TaskType.rate_summary: protocol_schema.RateSummaryTask,
            TaskType.initial_prompt: protocol_schema.InitialPromptTask,
            TaskType.user_reply: protocol_schema.UserReplyTask,
            TaskType.assistant_reply: protocol_schema.AssistantReplyTask,
            TaskType.rank_initial_prompts: protocol_schema.RankInitialPromptsTask,
            TaskType.rank_user_replies: protocol_schema.RankUserRepliesTask,
            TaskType.rank_assistant_replies: protocol_schema.RankAssistantRepliesTask,
            TaskType.done: protocol_schema.TaskDone,
        }
        self.task_models_map = task_models_map

    def post(self, path: str, json: dict) -> dict:
        response = requests.post(f"{self.backend_url}{path}", json=json, headers={"X-API-Key": self.api_key})
        response.raise_for_status()
        return response.json()

    def _parse_task(self, data: dict) -> protocol_schema.Task:
        if not isinstance(data, dict):
            raise ValueError("dict expected")

        task_type = data.get("type")
        if task_type not in self.task_models_map:
            raise RuntimeError(f"Unsupported task type: {task_type}")

        return self.task_models_map[task_type].parse_obj(data)

    def fetch_task(
        self, task_type: protocol_schema.TaskRequestType, user: Optional[protocol_schema.User] = None
    ) -> protocol_schema.Task:
        req = protocol_schema.TaskRequest(type=task_type, user=user)
        data = self.post("/api/v1/tasks/", req.dict())
        return self._parse_task(data)

    def fetch_random_task(self, user: Optional[protocol_schema.User] = None) -> protocol_schema.Task:
        return self.fetch_task(protocol_schema.TaskRequestType.random, user)

    def ack_task(self, task_id: str, post_id: str) -> None:
        req = protocol_schema.TaskAck(post_id=post_id)
        return self.post(f"/api/v1/tasks/{task_id}/ack", req.dict())

    def nack_task(self, task_id: str, reason: str) -> None:
        req = protocol_schema.TaskNAck(reason=reason)
        return self.post(f"/api/v1/tasks/{task_id}/nack", req.dict())

    def post_interaction(self, interaction: protocol_schema.Interaction) -> protocol_schema.Task:
        data = self.post("/api/v1/tasks/interaction", interaction.dict())
        return self._parse_task(data)
