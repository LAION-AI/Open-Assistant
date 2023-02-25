from typing import Any

import pydantic


class Settings(pydantic.BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    allowed_worker_compat_hashes: list[str] = ["distilgpt2"]

    sse_retry_timeout: int = 15000
    update_alembic: bool = True
    alembic_retries: int = 5
    alembic_retry_timeout: int = 1

    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "postgres"

    database_uri: str | None = None

    @pydantic.validator("database_uri", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return pydantic.PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    db_pool_size: int = 75
    db_max_overflow: int = 20

    root_token: str = "1234"

    debug_api_keys: list[str] = []

    do_compliance_checks: bool = True
    compliance_check_interval: int = 60

    api_root: str = "https://inference.prod.open-assistant.io"

    allow_debug_auth: bool = False

    auth_info: bytes = b"NextAuth.js Generated Encryption Key"
    auth_salt: bytes = b""
    auth_length: int = 32
    auth_secret: bytes = b""
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 60

    auth_discord_client_id: str = ""
    auth_discord_client_secret: str = ""


settings = Settings()
