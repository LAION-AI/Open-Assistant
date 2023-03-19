# a basic fastapi server to run generation on HF models

import signal
import sys

import fastapi
import interface
import torch
import transformers
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from settings import settings

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


# add prometheus metrics at /metrics
@app.on_event("startup")
async def enable_prom_metrics():
    Instrumentator().instrument(app).expose(app)


def terminate_server(signum, frame):
    logger.warning(f"Signal {signum}. Terminating server...")
    sys.exit(0)


model: transformers.PreTrainedModel
tokenizer: transformers.PreTrainedTokenizer
use_gpu: bool = False


@app.on_event("startup")
async def load_models():
    global model, tokenizer, use_gpu
    signal.signal(signal.SIGINT, terminate_server)
    logger.warning(f"Loading model {settings.model_id}...")
    if "llama" in settings.model_id:
        tokenizer = transformers.LlamaTokenizer.from_pretrained(settings.model_id)
        model = transformers.LlamaForCausalLM.from_pretrained(settings.model_id)
    else:
        tokenizer = transformers.AutoTokenizer.from_pretrained(settings.model_id)
        model = transformers.AutoModelForCausalLM.from_pretrained(settings.model_id)
    if torch.cuda.is_available():
        logger.warning("Using GPU")
        use_gpu = True
        model = model.cuda()
    logger.warning("Model loaded")
    signal.signal(signal.SIGINT, signal.SIG_DFL)


@app.on_event("startup")
async def welcome_message():
    logger.warning("Server started")
    logger.warning("To stop the server, press Ctrl+C")


@app.post("/generate")
async def generate(request: interface.GenerateStreamRequest):
    global model, tokenizer, use_gpu
    prompt = request.inputs
    params = request.parameters.dict()
    params.pop("seed")
    params.pop("stop")
    params.pop("details")
    with torch.no_grad():
        ids = tokenizer.encode(prompt, return_tensors="pt")
        if use_gpu:
            ids = ids.cuda()
        output = model.generate(ids, **params)
        output = output.cpu()
        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"text": decoded}
