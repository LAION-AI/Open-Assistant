# -*- coding: utf-8 -*-
"""Simple REPL frontend."""

import requests
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str, api_key: str):
    """Simple REPL frontend."""

    def _post(path: str, json: dict) -> dict:
        response = requests.post(f"{backend_url}{path}", json=json, headers={"X-API-Key": api_key})
        response.raise_for_status()
        return response.json()

    typer.echo("Requesting work...")
    tasks = _post("/api/v1/tasks/", {"type": "generic"})
    while tasks:
        task = tasks.pop(0)
        match (task["type"]):
            case "summarize_story":
                typer.echo("Summarize the following story:")
                typer.echo(task["story"])

                # acknowledge task
                _post(f"/api/v1/tasks/{task['id']}/ack", {"type": "post_created", "post_id": "1234"})

                summary = typer.prompt("Enter your summary")

                # send interaction
                new_tasks = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_reply_to_post",
                        "post_id": "1234",
                        "user_post_id": "5678",
                        "text": summary,
                        "user_id": "1234",
                    },
                )
                tasks.extend(new_tasks)
            case "task_done":
                typer.echo("Task done!")
            case _:
                typer.echo(f"Unknown task type {task['type']}")


if __name__ == "__main__":
    app()
