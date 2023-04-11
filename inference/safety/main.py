# A FastAPI server to run the safety pipeline

import fastapi
import uvicorn
from blade2blade import Blade2Blade
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_shared.schemas import inference
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


pipeline_loaded: bool = False
pipeline: Blade2Blade


@app.on_event("startup")
async def load_pipeline():
    global pipeline_loaded, pipeline
    pipeline = Blade2Blade(settings.safety_model_name)
    # warmup
    input = "|prompter|Hey,how are you?|endoftext|"
    _ = pipeline.predict(input)
    pipeline_loaded = True


@app.post("/safety", response_model=inference.SafetyResponse)
async def safety(request: inference.SafetyRequest):
    global pipeline
    if not pipeline_loaded:
        raise fastapi.HTTPException(status_code=503, detail="Server not fully loaded")
    outputs = pipeline.predict(request.inputs)
    return inference.SafetyResponse(outputs=outputs)


@app.get("/health")
async def health():
    if not pipeline_loaded:
        raise fastapi.HTTPException(status_code=503, detail="Server not fully loaded")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
