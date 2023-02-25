"""Simple REPL frontend."""

import json
import time

import requests
import sseclient
import typer
from loguru import logger

app = typer.Typer()


@app.command()
def main(backend_url: str = "http://127.0.0.1:8000"):
    """Simple REPL client."""
    while True:
        try:
            # login
            auth_data = requests.get(f"{backend_url}/auth/login/debug", params={"username": "test1"}).json()
            assert auth_data["token_type"] == "bearer"
            bearer_token = auth_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {bearer_token}"}

            chat_data = requests.post(f"{backend_url}/chat", json={}, headers=auth_headers).json()
            chat_id = chat_data["id"]
            typer.echo(f"Chat ID: {chat_id}")
            parent_id = None
            while True:
                message = typer.prompt("User").strip()
                if not message:
                    continue

                # wait for stream to be ready
                # could implement a queue position indicator
                # could be implemented with long polling
                # but server load needs to be considered
                response = requests.post(
                    f"{backend_url}/chat/{chat_id}/message",
                    json={
                        "parent_id": parent_id,
                        "content": message,
                    },
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
                message_id = json.loads(next(events).data)["assistant_message"]["id"]
                for event in events:
                    try:
                        data = json.loads(event.data)
                    except json.JSONDecodeError:
                        typer.echo(f"Failed to decode event data: {event.data}")
                        raise
                    if error := data.get("error"):
                        raise Exception(error)
                    print(data["token"]["text"], end="", flush=True)
                print()
                parent_id = message_id
        except typer.Abort:
            typer.echo("Exiting...")
            break
        except Exception as e:
            logger.exception("Chat Error")
            typer.echo(f"Error: {e}")
            typer.echo("Error, restarting chat...")
            time.sleep(1)


if __name__ == "__main__":
    app()
