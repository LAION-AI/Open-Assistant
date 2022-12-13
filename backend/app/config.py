# -*- coding: utf-8 -*-
# touch
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "open-chatGPT backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URI: Optional[PostgresDsn] = None

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    UPDATE_ALEMBIC: bool = True

    PORT: int = 8000
    FASTAPI_RELOAD: bool = False
    UVICONR_WOWKERS: int = 1

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings(_env_file=".env")
