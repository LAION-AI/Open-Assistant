# a basic fastapi server to run generation on HF models

import sys
import threading
from queue import Queue

import fastapi
import hf_streamer
import interface
import torch
import transformers
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_shared import model_configs
from settings import settings
from sse_starlette.sse import EventSourceResponse

app = fastapi.FastAPI()


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_exceptions(request: fastapi.Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Exception in request")
        raise
    return response


model_loaded: bool = False
fully_loaded: bool = False
model_input_queue: Queue = Queue()


def model_thread():
    model: transformers.PreTrainedModel
    tokenizer: transformers.PreTrainedTokenizer
    model, tokenizer = load_models()

    request: interface.GenerateStreamRequest
    output_queue: Queue
    # eos_token = ""
    # if hasattr(tokenizer, "eos_token"):
    #     eos_token = tokenizer.eos_token
    eos_token_id = None
    if hasattr(tokenizer, "eos_token_id"):
        eos_token_id = tokenizer.eos_token_id
    while True:
        request, output_queue = model_input_queue.get()
        try:
            prompt = request.inputs
            params = request.parameters.dict()
            seed = params.pop("seed")
            params.pop("stop")
            params.pop("details")

            def print_text(token_id: int):
                stream_response = interface.GenerateStreamResponse(
                    token=interface.Token(text="", id=token_id),
                )
                output_queue.put_nowait(stream_response)

            with torch.no_grad():
                ids = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=False)
                streamer = hf_streamer.HFStreamer(input_ids=ids, printer=print_text)
                ids = ids.to(model.device)
                output = model.generate(ids, **params, streamer=streamer, eos_token_id=eos_token_id)
                output = output.cpu()
                output_ids = output[0][len(ids[0]) :]
                decoded = tokenizer.decode(output_ids, skip_special_tokens=True)

            stream_response = interface.GenerateStreamResponse(
                token=interface.Token(
                    text="",  # hack because the "normal" inference server does this at once
                    id=0,
                ),
                generated_text=decoded.strip(),
                details=interface.StreamDetails(
                    finish_reason="eos_token",
                    generated_tokens=len(output_ids),
                    seed=seed,
                ),
            )
            output_queue.put_nowait(stream_response)
        except Exception as e:
            logger.exception("Exception in model thread")
            output_queue.put_nowait(interface.GenerateStreamResponse(error=str(e)))


def load_models():
    global model_loaded

    model_config = model_configs.MODEL_CONFIGS.get(settings.model_config_name)
    if model_config is None:
        logger.error(f"Unknown model config name: {settings.model_config_name}")
        sys.exit(2)

    logger.warning(f"Loading model {model_config.model_id}...")
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_config.model_id)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_config.model_id, torch_dtype="auto", load_in_8bit=settings.quantize, device_map="auto"
    )
    logger.warning("Model loaded")

    model_loaded = True

    return model, tokenizer


@app.on_event("startup")
async def start_model_thread():
    logger.warning("Starting model thread...")
    threading.Thread(target=model_thread, daemon=True).start()
    logger.warning("Model thread started")


@app.on_event("startup")
async def use_model_once():
    logger.warning("Generating once to warm up the model...")
    await generate(
        interface.GenerateStreamRequest(
            inputs="Hello world",
            parameters=interface.GenerateStreamParameters(
                max_new_tokens=10,
            ),
        )
    )
    logger.warning("Model warmed up")


@app.on_event("startup")
async def welcome_message():
    global fully_loaded
    logger.warning("Server started")
    logger.warning("To stop the server, press Ctrl+C")
    fully_loaded = True


@app.post("/generate_stream")
async def generate(
    request: interface.GenerateStreamRequest,
):
    async def event_stream():
        try:
            output_queue: Queue = Queue()
            model_input_queue.put_nowait((request, output_queue))
            while True:
                output = output_queue.get()  # type: interface.GenerateStreamResponse
                logger.debug(f"Sending output: {output}")
                yield {"data": output.json()}
                if output.is_end:
                    break
                if output.is_error:
                    raise Exception(output.error)
        except Exception as e:
            logger.exception("Exception in event stream")
            output_queue.put_nowait(interface.GenerateStreamResponse(error=str(e)))
            raise

    return EventSourceResponse(event_stream())


@app.get("/health")
async def health():
    if not (fully_loaded and model_loaded):
        raise fastapi.HTTPException(status_code=503, detail="Server not fully loaded")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
