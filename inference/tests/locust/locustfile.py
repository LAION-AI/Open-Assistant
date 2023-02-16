from locust import HttpUser, between


class ChatUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post("/chat", json={}).json()
        self.chat_id = response["id"]
