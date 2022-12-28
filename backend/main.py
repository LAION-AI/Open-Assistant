# -*- coding: utf-8 -*-
from pathlib import Path

import alembic.command
import alembic.config
import fastapi
from loguru import logger
from oasst_backend.api.v1.api import api_router
from oasst_backend.config import settings
from oasst_backend.exceptions import OasstError
from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")


@app.exception_handler(OasstError)
async def http_exception_handler(request: fastapi.Request, ex: OasstError):
    logger.error(f"{request.method} {request.url} failed: {repr(ex)}")
    return fastapi.responses.JSONResponse(
        status_code=ex.http_status_code, content={"message": ex.message, "error_code": ex.error_code}
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.UPDATE_ALEMBIC:

    @app.on_event("startup")
    def alembic_upgrade():
        logger.info("Attempting to upgrade alembic on startup")
        try:
            alembic_ini_path = Path(__file__).parent / "alembic.ini"
            alembic_cfg = alembic.config.Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URI)
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("Successfully upgraded alembic on startup")
        except Exception:
            logger.exception("Alembic upgrade failed on startup")


app.include_router(api_router, prefix=settings.API_V1_STR)
