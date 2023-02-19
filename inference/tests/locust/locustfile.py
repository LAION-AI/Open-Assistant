import json

import sseclient
from locust import HttpUser, between, task


class ChatUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post("/chat", json={}).json()
        self.chat_id = response["id"]

    @task
    def send_msg(self):
        response = self.client.post(
            f"/chat/{self.chat_id}/message",
            json={"message": "yo"},
            stream=True,
            headers={"Accept": "text/event-stream"},
        )
        response.raise_for_status()

        client = sseclient.SSEClient(response)
        for event in client.events():
            _ = json.loads(event.data)
