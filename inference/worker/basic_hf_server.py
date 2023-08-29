"""
Basic FastAPI server to serve models using HuggingFace Transformers library.
This is an alternative to running the HuggingFace `text-generation-inference` (tgi) server.
"""

import sys
import threading
from queue import Queue

import fastapi
import hf_stopping
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

DECODE_TOKEN = "<decode-token>"


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
    """Continually obtain new work requests from the model input queue and work on them."""
    model: transformers.PreTrainedModel
    tokenizer: transformers.PreTrainedTokenizer
    model, tokenizer, decode_token = load_models()

    request: interface.GenerateStreamRequest
    output_queue: Queue
    eos_token_id = tokenizer.eos_token_id if hasattr(tokenizer, "eos_token_id") else None
    while True:
        request, output_queue = model_input_queue.get()
        try:
            prompt = request.inputs
            params = request.parameters.dict()
            seed = params.pop("seed")
            stop_sequences = params.pop("stop")
            params.pop("details")
            params.pop("plugins")

            if seed is not None:
                torch.manual_seed(seed)

            last_token_id = None  # need to delay by 1 to simulate tgi

            def print_text(token_id: int):
                nonlocal last_token_id
                if last_token_id is not None:
                    text = decode_token(last_token_id)
                    stream_response = interface.GenerateStreamResponse(
                        token=interface.Token(text=text, id=last_token_id),
                    )
                    output_queue.put_nowait(stream_response)
                last_token_id = token_id

            with torch.no_grad():
                ids = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=False)
                streamer = hf_streamer.HFStreamer(input_ids=ids, printer=print_text)
                ids = ids.to(model.device)
                stopping_criteria = (
                    transformers.StoppingCriteriaList(
                        [hf_stopping.SequenceStoppingCriteria(tokenizer, stop_sequences, prompt)]
                    )
                    if stop_sequences
                    else None
                )
                output = model.generate(
                    ids,
                    **params,
                    streamer=streamer,
                    eos_token_id=eos_token_id,
                    stopping_criteria=stopping_criteria,
                )
                output = output.cpu()
                output_ids = output[0][len(ids[0]) :]
                decoded = tokenizer.decode(output_ids, skip_special_tokens=True)

            stream_response = interface.GenerateStreamResponse(
                token=interface.Token(
                    text=decode_token(last_token_id),  # hack because the "normal" inference server does this at once
                    id=last_token_id,
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

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)

    model_config = model_configs.MODEL_CONFIGS.get(settings.model_config_name)
    if model_config is None:
        logger.error(f"Unknown model config name: {settings.model_config_name}")
        sys.exit(2)

    hf_config = transformers.AutoConfig.from_pretrained(model_config.model_id)
    logger.warning(f"Loading model {model_config.model_id}...")
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_config.model_id)
    logger.warning(f"tokenizer {tokenizer.name_or_path} has vocab size {len(tokenizer)}")

    # see `decode_token` method, taken from HF text-generation-inference
    tokenizer.add_special_tokens({"additional_special_tokens": ["<decode-token>"]})

    special_decode_token_id = tokenizer.convert_tokens_to_ids("<decode-token>")
    special_decode_token_length = len("<decode-token>")

    def decode_token(token_id):
        result = tokenizer.decode([special_decode_token_id, token_id], skip_special_tokens=False)
        # slice to remove special decode token
        return result[special_decode_token_length:]

    config_dtype = hf_config.torch_dtype if hasattr(hf_config, "torch_dtype") else torch.float32
    dtype = torch.bfloat16 if torch.has_cuda and torch.cuda.is_bf16_supported() else config_dtype

    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_config.model_id,
        torch_dtype=dtype,
        load_in_8bit=settings.quantize,
        device_map="auto" if torch.cuda.is_available() else None,
    ).eval()
    logger.warning("Model loaded, using it once...")

    # warmup
    with torch.no_grad():
        text = "Hello, world"
        tokens = tokenizer.encode(text, return_tensors="pt")
        tokens = tokens.to(model.device)
        model.generate(tokens, max_length=10, num_beams=1, do_sample=False)

    model_loaded = True

    return model, tokenizer, decode_token


@app.on_event("startup")
async def start_model_thread():
    logger.warning("Starting model thread...")
    threading.Thread(target=model_thread, daemon=True).start()
    logger.warning("Model thread started")


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
    def event_stream():
        try:
            output_queue: Queue = Queue()
            model_input_queue.put_nowait((request, output_queue))
            while True:
                output = output_queue.get()  # type: interface.GenerateStreamResponse
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
