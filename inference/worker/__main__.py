import json

import rel
import requests
import sseclient
import typer
import websocket
from loguru import logger
from oasst_shared.schemas import inference, protocol

app = typer.Typer()


@app.command()
def main(
    backend_url: str = "ws://localhost:8000",
    model_name: str = "distilgpt2",
    inference_server_url: str = "http://localhost:8001",
):
    def on_open(ws: websocket.WebSocket):
        worker_config = inference.WorkerConfig(model_name=model_name)
        ws.send(worker_config.json())

    def on_message(ws: websocket.WebSocket, message: str):
        # TODO: what if this comes in, but one is already in progress?
        # also need to think of enabling batching
        work_request = inference.WorkRequest.parse_raw(message)

        def _prepare_message(message: protocol.ConversationMessage) -> str:
            prefix = "Assistant: " if message.is_assistant else "User: "
            return prefix + message.text

        # construct prompt
        messages = [_prepare_message(message) for message in work_request.conversation.messages]

        prefix = (
            "The following is a conversation between a user and an assistant. "
            "The assistant is helpful, creative, clever, and very friendly.\n"
            "Assistant: Hello! How can I help you today?\n"
        )

        prompt = prefix + "\n".join(messages) + "\nAssistant:"

        # TODO: use the seed
        # torch.manual_seed(work_request.seed)
        # model_output = pipe(prompt, max_new_tokens=work_request.max_new_tokens, do_sample=True, return_full_text=False)[
        #     0
        # ]["generated_text"]
        # model_output = model_output.strip()

        # # fake streaming
        # split_idcs = [m.start() for m in re.finditer(r"([\w:]+)", model_output)]
        # pieces = [model_output[a:b] for a, b in zip([0] + split_idcs, split_idcs + [None])]
        # for piece in pieces:
        #     if not piece:
        #         continue
        #     if piece.strip() in ("User:", "Assistant:"):
        #         break
        #     ws.send(inference.WorkResponsePacket(token=piece).json())
        #     time.sleep(0.1)
        # ws.send(inference.WorkResponsePacket(is_end=True).json())

        response = requests.post(
            f"{inference_server_url}/generate_stream",
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": work_request.max_new_tokens,
                    "do_sample": work_request.do_sample,
                    "top_k": work_request.top_k,
                    "top_p": work_request.top_p,
                    "temperature": work_request.temperature,
                },
            },
            stream=True,
            headers={"Accept": "text/event-stream"},
        )
        response.raise_for_status()

        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            if data["is_end"]:
                break
            intermediate = data["event"]
            ws.send(inference.WorkResponsePacket(token=intermediate["token"]).json())
        ws.send(inference.WorkResponsePacket(is_end=True).json())

    def on_error(ws: websocket.WebSocket, error: Exception):
        logger.error(f"Connection error: {error}")

    def on_close(ws: websocket.WebSocket, close_status_code: int, close_msg: str):
        logger.warning(f"Connection closed: {close_status_code=} {close_msg=}")

    ws = websocket.WebSocketApp(
        f"{backend_url}/work",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )

    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()


if __name__ == "__main__":
    app()
