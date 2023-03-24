# a basic fastapi server to run generation on HF models

import signal
import sys

import fastapi
import interface
import torch
import transformers
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_shared import model_configs
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


def terminate_server(signum, frame):
    logger.warning(f"Signal {signum}. Terminating server...")
    sys.exit(0)


model: transformers.PreTrainedModel
tokenizer: transformers.PreTrainedTokenizer


@app.on_event("startup")
async def load_models():
    global model, tokenizer
    signal.signal(signal.SIGINT, terminate_server)

    model_config = model_configs.MODEL_CONFIGS.get(settings.model_config_name)
    if model_config is None:
        logger.error(f"Unknown model config name: {settings.model_config_name}")
        sys.exit(2)

    logger.warning(f"Loading model {model_config.model_id}...")
    if model_config.is_llama:
        config = transformers.LlamaConfig.from_pretrained(model_config.model_id)
        tokenizer = transformers.LlamaTokenizer.from_pretrained(model_config.model_id)
        model = transformers.LlamaForCausalLM.from_pretrained(model_config.model_id, torch_dtype=config.torch_dtype)
    else:
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_config.model_id)
        model = transformers.AutoModelForCausalLM.from_pretrained(model_config.model_id)
    if torch.cuda.is_available():
        logger.warning("Using GPU")
        model = model.cuda()
    logger.warning("Model loaded")
    signal.signal(signal.SIGINT, signal.SIG_DFL)


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
    logger.warning("Server started")
    logger.warning("To stop the server, press Ctrl+C")


@app.post("/generate")
async def generate(request: interface.GenerateStreamRequest):
    global model, tokenizer
    prompt = request.inputs
    params = request.parameters.dict()
    params.pop("seed")
    params.pop("stop")
    params.pop("details")
    with torch.no_grad():
        ids = tokenizer.encode(prompt, return_tensors="pt")
        ids = ids.to(model.device)
        output = model.generate(ids, **params)
        output = output.cpu()
        output_ids = output[0][len(ids[0]) :]
        decoded = tokenizer.decode(output_ids, skip_special_tokens=True)
    return {"text": decoded.strip()}


@app.get("/health")
async def health():
    return {"status": "ok"}
