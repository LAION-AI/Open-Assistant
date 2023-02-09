"""Simple REPL frontend."""

import http
import random

import requests
import typer

app = typer.Typer()


# debug constants
USER = {"id": "1234", "display_name": "John Doe", "auth_method": "local"}


def _random_message_id():
    return str(random.randint(1000, 9999))


def _render_message(message: dict) -> str:
    """Render a message to the user."""
    if message["is_assistant"]:
        return f"Assistant: {message['text']}"
    return f"Prompter: {message['text']}"


@app.command()
def main(backend_url: str = "http://127.0.0.1:8080", api_key: str = "1234"):
    """Simple REPL frontend."""

    # make sure dummy user has accepted the terms of service
    create_user_request = dict(USER)
    create_user_request["tos_acceptance"] = True
    response = requests.post(
        f"{backend_url}/api/v1/frontend_users/", json=create_user_request, headers={"X-API-Key": api_key}
    )
    response.raise_for_status()
    user = response.json()
    typer.echo(f"user: {user}")

    def _post(path: str, json: dict) -> dict:
        response = requests.post(f"{backend_url}{path}", json=json, headers={"X-API-Key": api_key})
        response.raise_for_status()
        if response.status_code == http.HTTPStatus.NO_CONTENT:
            return None
        return response.json()

    typer.echo("Requesting work...")
    tasks = [_post("/api/v1/tasks/", {"type": "random", "user": USER})]
    while tasks:
        task = tasks.pop(0)
        match (task["type"]):
            case "summarize_story":
                typer.echo("Summarize the following story:")
                typer.echo(task["story"])

                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                summary = typer.prompt("Enter your summary")

                user_message_id = _random_message_id()

                # send interaction
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_reply_to_message",
                        "message_id": message_id,
                        "task_id": task["id"],
                        "user_message_id": user_message_id,
                        "text": summary,
                        "user": USER,
                    },
                )
                tasks.append(new_task)
            case "rate_summary":
                typer.echo("Rate the following summary:")
                typer.echo(task["summary"])
                typer.echo("Full text:")
                typer.echo(task["full_text"])
                typer.echo(f"Rating scale: {task['scale']['min']} - {task['scale']['max']}")

                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                rating = typer.prompt("Enter your rating", type=int)
                # send interaction
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "message_rating",
                        "message_id": message_id,
                        "rating": rating,
                        "user": USER,
                    },
                )
                tasks.append(new_task)
            case "initial_prompt":
                typer.echo("Please provide an initial prompt to the assistant.")
                if task["hint"]:
                    typer.echo(f"Hint: {task['hint']}")
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})
                prompt = typer.prompt("Enter your prompt")
                user_message_id = _random_message_id()
                # send interaction
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_reply_to_message",
                        "message_id": message_id,
                        "task_id": task["id"],
                        "user_message_id": user_message_id,
                        "text": prompt,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "prompter_reply":
                typer.echo("Please provide a reply to the assistant.")
                typer.echo("Here is the conversation so far:")
                for message in task["conversation"]["messages"]:
                    typer.echo(_render_message(message))
                if task["hint"]:
                    typer.echo(f"Hint: {task['hint']}")
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})
                reply = typer.prompt("Enter your reply")
                user_message_id = _random_message_id()
                # send interaction
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_reply_to_message",
                        "message_id": message_id,
                        "user_message_id": user_message_id,
                        "text": reply,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "assistant_reply":
                typer.echo("Act as the assistant and reply to the user.")
                typer.echo("Here is the conversation so far:")
                for message in task["conversation"]["messages"]:
                    typer.echo(_render_message(message))
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})
                reply = typer.prompt("Enter your reply")
                user_message_id = _random_message_id()
                # send interaction
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_reply_to_message",
                        "message_id": message_id,
                        "task_id": task["id"],
                        "user_message_id": user_message_id,
                        "text": reply,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "rank_initial_prompts":
                typer.echo("Rank the following prompts:")
                for idx, prompt in enumerate(task["prompts"], start=1):
                    typer.echo(f"{idx}: {prompt}")
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                ranking_str = typer.prompt("Enter the prompt numbers in order of preference, separated by commas")
                ranking = [int(x) - 1 for x in ranking_str.split(",")]

                # send ranking
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "message_ranking",
                        "message_id": message_id,
                        "ranking": ranking,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "rank_prompter_replies" | "rank_assistant_replies":
                typer.echo("Here is the conversation so far:")
                for message in task["conversation"]["messages"]:
                    typer.echo(_render_message(message))
                typer.echo("Rank the following replies:")
                for idx, reply in enumerate(task["replies"], start=1):
                    typer.echo(f"{idx}: {reply}")
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                ranking_str = typer.prompt("Enter the reply numbers in order of preference, separated by commas")
                ranking = [int(x) - 1 for x in ranking_str.split(",")]

                # send labels
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "message_ranking",
                        "message_id": message_id,
                        "task_id": task["id"],
                        "ranking": ranking,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "label_initial_prompt":
                typer.echo("Label the following prompt:")
                typer.echo(task["prompt"])
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                valid_labels = task["valid_labels"]

                labels_dict = None
                if task["mode"] == "simple" and len(valid_labels) == 1:
                    answer: str = typer.confirm(f"{valid_labels[0]}?")
                    labels_dict = {valid_labels[0]: 1 if answer else 0}
                else:
                    while labels_dict is None:
                        labels_str: str = typer.prompt("Enter labels, separated by commas")
                        labels = labels_str.lower().replace(" ", "").split(",")

                        if all([label in valid_labels for label in labels]):
                            labels_dict = {label: "1" if label in labels else "0" for label in valid_labels}
                        else:
                            invalid_labels = [label for label in labels if label not in valid_labels]
                            typer.echo(f"Invalid labels: {', '.join(invalid_labels)}. Valid: {', '.join(valid_labels)}")

                # send labels
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_labels",
                        "message_id": task["message_id"],
                        "task_id": task["id"],
                        "text": task["prompt"],
                        "labels": labels_dict,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "label_prompter_reply" | "label_assistant_reply":
                typer.echo("Here is the conversation so far:")
                for message in task["conversation"]["messages"]:
                    typer.echo(_render_message(message))

                typer.echo("Label the following reply:")
                typer.echo(task["reply"])
                # acknowledge task
                message_id = _random_message_id()
                _post(f"/api/v1/tasks/{task['id']}/ack", {"message_id": message_id})

                valid_labels = task["valid_labels"]

                labels_dict = None
                if task["mode"] == "simple" and len(valid_labels) == 1:
                    answer: str = typer.confirm(f"{valid_labels[0]}?")
                    labels_dict = {valid_labels[0]: 1 if answer else 0}
                else:
                    while labels_dict is None:
                        labels_str: str = typer.prompt("Enter labels, separated by commas")
                        labels = labels_str.lower().replace(" ", "").split(",")

                        if all([label in valid_labels for label in labels]):
                            labels_dict = {label: "1" if label in labels else "0" for label in valid_labels}
                        else:
                            invalid_labels = [label for label in labels if label not in valid_labels]
                            typer.echo(f"Invalid labels: {', '.join(invalid_labels)}. Valid: {', '.join(valid_labels)}")

                # send labels
                new_task = _post(
                    "/api/v1/tasks/interaction",
                    {
                        "type": "text_labels",
                        "message_id": task["message_id"],
                        "task_id": task["id"],
                        "text": task["reply"],
                        "labels": labels_dict,
                        "user": USER,
                    },
                )
                tasks.append(new_task)

            case "task_done":
                typer.echo("Task done!")
            case _:
                typer.echo(f"Unknown task type {task['type']}")


if __name__ == "__main__":
    app()
