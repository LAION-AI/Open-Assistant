import json
import random
import string
import time

import sseclient
from locust import HttpUser, between, task


class ChatUser(HttpUser):
    wait_time = between(1, 2)
    conversation_length = random.randint(3, 20)
    time_to_respond = random.randint(3, 5)  # for the user

    @task
    def chat(self):
        # login
        auth_data = self.client.get(
            "/auth/login/debug", params={"username": "".join(random.choice(string.ascii_lowercase) for _ in range(20))}
        ).json()
        assert auth_data["token_type"] == "bearer"
        bearer_token = auth_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {bearer_token}"}

        chat_data = self.client.post("/chats", json={}, headers=auth_headers).json()
        chat_id = chat_data["id"]
        parent_id = None

        for _ in range(self.conversation_length):
            response = self.client.post(
                f"/chats/{chat_id}/messages",
                json={
                    "parent_id": parent_id,
                    "content": "hello",
                },
                headers=auth_headers,
            )
            response.raise_for_status()
            message_id = response.json()["assistant_message"]["id"]

            response = self.client.get(
                f"/chats/{chat_id}/messages/{message_id}/events",
                stream=True,
                headers={
                    "Accept": "text/event-stream",
                    **auth_headers,
                },
            )
            response.raise_for_status()

            client = sseclient.SSEClient(response)
            print("Assistant: ", end="", flush=True)
            events = iter(client.events())
            for event in events:
                if event.event == "error":
                    raise Exception(event.data)
                if event.event == "ping":
                    continue
                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    raise
                if error := data.get("error"):
                    raise Exception(error)
            parent_id = message_id

            time.sleep(self.time_to_respond)
