import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from loguru import logger

from oasst_backend.config import settings
from oasst_backend.exceptions import OasstError
from oasst_backend.api.v1.api import api_router

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")
if settings.BACKEND_CORS_ORIGINS:
app.add_middleware(
CORSMiddleware,
allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
allow_credentials=True,
allow_methods=[""],
allow_headers=[""],
)

@app.exception_handler(OasstError)
def oasst_exception_handler(request, exc):
logger.error(f"{request.method} {request.url} failed: {exc}")
return JSONResponse(
status_code=exc.http_status_code,
content={"message": exc.message, "error_code": exc.error_code},
)

@app.exception_handler(Exception)
def unhandled_exception_handler(request, exc):
logger.exception(f"{request.method} {request.url} failed [UNHANDLED]: {exc}")
status_code = 500
return JSONResponse(
status_code=status_code,
content={"message": "Internal Server Error", "error_code": "GENERIC_ERROR"},
)

if settings.UPDATE_ALEMBIC:
from alembic import command, config
@app.on_event("startup")
def alembic_upgrade():
    logger.info("Attempting to upgrade alembic on startup")
    try:
        alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
        alembic_cfg = config.Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URI)
        command.upgrade(alembic_cfg, "head")
        logger.info("Successfully upgraded alembic on startup")
    except Exception:
        logger.exception("Alembic upgrade failed on startup")

