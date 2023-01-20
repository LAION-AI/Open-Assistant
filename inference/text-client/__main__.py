"""Simple REPL frontend."""

import json

import requests
import sseclient
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "http://127.0.0.1:8000"):
    """Simple REPL client."""
    while True:
        prompt = typer.prompt("Enter text to complete").strip()
        queue_id = requests.post(f"{backend_url}/complete", json={"text": prompt}).json()

        headers = {"Accept": "text/event-stream"}
        response = requests.get(f"{backend_url}/stream/{queue_id}", stream=True, headers=headers)

        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            print(data["token"], end="", flush=True)
        print()


if __name__ == "__main__":
    app()
