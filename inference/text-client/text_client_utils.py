import json

import requests
import sseclient
from loguru import logger


class DebugClient:
    def __init__(self, backend_url, http_client=requests):
        self.backend_url = backend_url
        self.http_client = http_client

    def login(self, username):
        auth_data = self.http_client.get(f"{self.backend_url}/auth/callback/debug", params={"code": username}).json()
        assert auth_data["access_token"]["token_type"] == "bearer"
        bearer_token = auth_data["access_token"]["access_token"]
        logger.debug(f"Logged in as {username} with token {bearer_token}")
        self.auth_headers = {"Authorization": f"Bearer {bearer_token}"}

    def create_chat(self):
        response = self.http_client.post(
            f"{self.backend_url}/chats",
            json={},
            headers=self.auth_headers,
        )
        response.raise_for_status()
        self.chat_id = response.json()["id"]
        self.message_id = None
        return self.chat_id

    def send_message(self, message, model_config_name):
        response = self.http_client.post(
            f"{self.backend_url}/chats/{self.chat_id}/prompter_message",
            json={
                "parent_id": self.message_id,
                "content": message,
            },
            headers=self.auth_headers,
        )
        response.raise_for_status()
        prompter_message_id = response.json()["id"]

        response = self.http_client.post(
            f"{self.backend_url}/chats/{self.chat_id}/assistant_message",
            json={
                "parent_id": prompter_message_id,
                "model_config_name": model_config_name,
                "sampling_parameters": {
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.2,
                    "temperature": 1.0,
                },
            },
            headers=self.auth_headers,
        )
        response.raise_for_status()
        self.message_id = response.json()["id"]

        response = self.http_client.get(
            f"{self.backend_url}/chats/{self.chat_id}/messages/{self.message_id}/events",
            stream=True,
            headers={
                "Accept": "text/event-stream",
                **self.auth_headers,
            },
        )
        response.raise_for_status()
        if response.status_code == 204:
            response = self.http_client.get(
                f"{self.backend_url}/chats/{self.chat_id}/messages/{self.message_id}",
                headers=self.auth_headers,
            )
            response.raise_for_status()
            data = response.json()
            yield data["content"]
        else:
            client = sseclient.SSEClient(response)
            events = iter(client.events())
            for event in events:
                if event.event == "error":
                    raise RuntimeError(event.data)
                if event.event == "ping":
                    continue
                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    raise RuntimeError(f"Failed to decode {event.data=}")
                event_type = data["event_type"]
                if event_type == "token":
                    yield data["text"]
                elif event_type == "message":
                    # full message content, can be ignored here
                    break
                elif event_type == "error":
                    raise RuntimeError(data["error"])
                elif event_type == "pending":
                    logger.debug(f"Message pending. {data=}")
