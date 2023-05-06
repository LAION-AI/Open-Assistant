"""Simple REPL frontend."""

import time

import text_client_utils as utils
import typer
from loguru import logger

app = typer.Typer()


@app.command()
def main(backend_url: str = "http://127.0.0.1:8000", model_config_name="distilgpt2", username="test1"):
    """Simple REPL client."""
    while True:
        try:
            # login
            client = utils.DebugClient(backend_url)
            client.login(username)
            chat_id = client.create_chat()
            typer.echo(f"Chat ID: {chat_id}")
            while True:
                message = typer.prompt("User").strip()
                if not message:
                    continue

                events = client.send_message(message, model_config_name)
                print("Assistant: ", end="", flush=True)
                for event in events:
                    print(event, end="", flush=True)
                print()

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
