import json
import random
import time

import sseclient
from locust import HttpUser, between, task


class ChatUser(HttpUser):
    wait_time = between(1, 2)
    conversation_length = random.randint(3, 20)
    time_to_respond = random.randint(3, 5)  # for the user

    @task
    def chat(self):
        chat_id = self.client.post("/chat", json={}).json()["id"]

        for _ in range(self.conversation_length):
            response = self.client.post(
                f"/chat/{chat_id}/message",
                json={"message": "yo"},
                stream=True,
                headers={"Accept": "text/event-stream"},
            )
            response.raise_for_status()

            client = sseclient.SSEClient(response)
            for event in client.events():
                _ = json.loads(event.data)

            time.sleep(self.time_to_respond)
