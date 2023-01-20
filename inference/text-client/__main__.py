"""Simple REPL frontend."""

import json
import time

import requests
import sseclient
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "http://127.0.0.1:8000"):
    """Simple REPL client."""
    while True:
        prompt = typer.prompt("Enter text to complete").strip()
        complete_response = requests.post(f"{backend_url}/complete", json={"prompt": prompt}).json()
        completion_id = complete_response["completion_id"]

        # wait for stream to be ready
        # could implement a queue position indicator
        # could be implemented with long polling
        # but server load needs to be considered
        while True:
            headers = {"Accept": "text/event-stream"}
            response = requests.get(f"{backend_url}/stream/{completion_id}", stream=True, headers=headers)
            if response.status_code == 200:
                break
            time.sleep(0.25)

        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            print(data["token"], end="", flush=True)
        print()


if __name__ == "__main__":
    app()
