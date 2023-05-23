# a basic fastapi server to run generation on HF models

import sys
import threading
from queue import Queue

from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
import fastapi
import hf_streamer
import interface
import torch
import transformers
from transformers import AutoTokenizer, TextGenerationPipeline
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from hf_stopping import SequenceStoppingCriteria
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
                    transformers.StoppingCriteriaList([SequenceStoppingCriteria(tokenizer, stop_sequences, prompt)])
                    if stop_sequences
                    else None
                )
                # TODO: integrate back more of the original implementation
                #output = model.generate(
                #    ids,
                #    **params,
                #    streamer=streamer,
                #    eos_token_id=eos_token_id,
                #    stopping_criteria=stopping_criteria,
                #)
                output = model.generate(**params, input_ids=ids, streamer=streamer, stopping_criteria=stopping_criteria)
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
 
    logger.warning("Model loaded but using GPTQ 4bit quantization")

    # TODO: need transformers library fix and some extra installs
    #pretrained_model_dir = "/data/models--OpenAssistant--oasst-sft-7-llama-30b"
    quantized_model_dir = "/data/models--TheBloke--OpenAssistant-SFT-7-Llama-30B-GPTQ"
    tokenizer = AutoTokenizer.from_pretrained(quantized_model_dir, use_fast=True)
    hf_config = quantize_config = BaseQuantizeConfig(
        bits=4,  # quantize model to 4-bit
        group_size=128,  # it is recommended to set the value to 128
    )

    #examples = [
    #    tokenizer(
    #        "auto-gptq is an easy-to-use model quantization library with user-friendly apis, based on GPTQ algorithm."
    #    )
    #]
    # load un-quantized model, by default, the model will always be loaded into CPU memory
    #model = AutoGPTQForCausalLM.from_pretrained(pretrained_model_dir, quantize_config)
    # quantize model, the examples should be list of dict whose keys can only be "input_ids" and "attention_mask"
    #model.quantize(examples, use_triton=False)
    # save quantized model
    #model.save_quantized(quantized_model_dir)
    # save quantized model using safetensors
    #model.save_quantized(quantized_model_dir, use_safetensors=True)

    # load quantized model to the first GPU
    model = AutoGPTQForCausalLM.from_quantized(quantized_model_dir, device="cuda:0", use_triton=False,
                                               quantize_config=quantize_config, use_safetensors=True, model_basename="OpenAssistant-30B-epoch7-GPTQ-4bit-1024g.compat.no-act-order")

    logger.warning(f"tokenizer {tokenizer.name_or_path} has vocab size {tokenizer.vocab_size}")

    # see `decode_token` method, taken from HF text-generation-inference
    tokenizer.add_special_tokens({"additional_special_tokens": ["<decode-token>"]})

    special_decode_token_id = tokenizer.convert_tokens_to_ids("<decode-token>")
    special_decode_token_length = len("<decode-token>")

    def decode_token(token_id):
        result = tokenizer.decode([special_decode_token_id, token_id], skip_special_tokens=False)
        # slice to remove special decode token
        return result[special_decode_token_length:]

    logger.warning("Model loaded, using it once...")

    # warmup
    with torch.no_grad():
        text = "Hello, world"
        tokens = tokenizer.encode(text, return_tensors="pt")
        tokens = tokens.to(model.device)
        # TODO: model.generate has some incompatibility and trouble
        #model.generate(tokens, max_length=10, num_beams=1, do_sample=False)
        # original inference with model.generate
        #print(tokenizer.decode(model.generate(**tokenizer(text, return_tensors="pt").to("cuda:0"))[0]))
        # or you can also use pipeline
        from transformers import TextGenerationPipeline
        pipeline = TextGenerationPipeline(model=model, tokenizer=tokenizer)
        print(pipeline(text)[0]["generated_text"])

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
