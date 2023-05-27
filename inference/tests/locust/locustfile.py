import random
import string
from pathlib import Path

from locust import HttpUser, between, task

from ..text-client import text_client_utils as utils


class ChatUser(HttpUser):
    wait_time = between(1, 2)
    conversation_length = random.randint(3, 20)
    time_to_respond = random.randint(3, 5)  # for the user
    model_config_name = "_lorem"

    def on_start(self):
        self.client = utils.DebugClient(backend_url="", http_client=self.client)
        username = "".join(random.choice(string.ascii_lowercase) for _ in range(20))
        self.client.login(username)
        self.client.create_chat()

    @task
    def chat(self):
        for _ in range(self.conversation_length):
            self.client.send_message("hello", self.model_config_name)
            self.wait()

    def wait(self):
        self.client.wait()
        self.wait_time()


