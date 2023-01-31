"""Simple REPL frontend."""

import json

import requests
import sseclient
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "http://127.0.0.1:8000"):
    """Simple REPL client."""
    chat_id = requests.post(f"{backend_url}/chat", json={}).json()["id"]
    while True:
        message = typer.prompt("User").strip()

        # wait for stream to be ready
        # could implement a queue position indicator
        # could be implemented with long polling
        # but server load needs to be considered
        response = requests.post(
            f"{backend_url}/chat/{chat_id}/message",
            json={"message": message},
            stream=True,
            headers={"Accept": "text/event-stream"},
        )
        response.raise_for_status()

        client = sseclient.SSEClient(response)
        print("Assistant: ", end="", flush=True)
        for event in client.events():
            data = json.loads(event.data)
            print(data["token"], end="", flush=True)
        print()


if __name__ == "__main__":
    app()
