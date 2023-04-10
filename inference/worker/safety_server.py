# A FastAPI server to run the safety pipeline

import fastapi
import interface
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

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
pipeline: ...


@app.on_event("startup")
async def load_pipeline():
    global pipeline_loaded, pipeline
    # TODO
    pipeline = ...
    pipeline_loaded = True


@app.post("/safety")
async def safety(request: interface.SafetyRequest):
    global pipeline
    # TODO
    outputs = pipeline(request.inputs)
    return interface.SafetyResponse(outputs=outputs)


@app.get("/health")
async def health():
    if not pipeline_loaded:
        raise fastapi.HTTPException(status_code=503, detail="Server not fully loaded")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
