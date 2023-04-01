from typing import Any

import pydantic


class Settings(pydantic.BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    message_queue_expire: int = 60
    work_queue_max_size: int | None = None

    allowed_worker_compat_hashes: str = "*"

    @property
    def allowed_worker_compat_hashes_list(self) -> list[str]:
        return self.allowed_worker_compat_hashes.split(",")

    allowed_model_config_names: str = "*"

    @property
    def allowed_model_config_names_list(self) -> list[str]:
        return self.allowed_model_config_names.split(",")

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
            scheme="postgresql+asyncpg",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    db_pool_size: int = 75
    db_max_overflow: int = 20
    db_echo: bool = False

    root_token: str = "1234"

    debug_api_keys: str = ""

    @property
    def debug_api_keys_list(self) -> list[str]:
        return self.debug_api_keys.split(",")

    do_compliance_checks: bool = False
    compliance_check_interval: int = 60
    compliance_check_timeout: int = 60

    # this is the URL which will be redirected to when authenticating with oauth2
    # we decided on letting the nextjs / website backend handle the token at first
    # and then proxy this information back to the inference server
    # in short: this should refer to the website, not to this server
    auth_callback_root: str = "http://localhost:3000/api/inference_auth"

    allow_debug_auth: bool = False

    auth_info: bytes = b"NextAuth.js Generated Encryption Key"
    auth_salt: bytes = b""
    auth_length: int = 32
    auth_secret: bytes = b""
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 60
    auth_refresh_token_expire_minutes: int = 60 * 24 * 7

    auth_discord_client_id: str = ""
    auth_discord_client_secret: str = ""

    auth_github_client_id: str = ""
    auth_github_client_secret: str = ""

    pending_event_interval: int = 1
    worker_ping_interval: int = 3

    assistant_message_timeout: int = 60

    inference_cors_origins: str = "*"

    @property
    def inference_cors_origins_list(self) -> list[str]:
        return self.inference_cors_origins.split(",")


settings = Settings()
