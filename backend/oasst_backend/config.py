from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from oasst_shared.schemas import protocol as protocol_schema
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, FilePath, PostgresDsn, validator


class TreeManagerConfiguration(BaseModel):
    """TreeManager configuration settings"""

    max_active_trees: int = 10
    """Maximum number of concurrently active message trees in the database.
    No new initial prompt tasks are handed out to users if this
    number is reached."""

    max_tree_depth: int = 6
    """Maximum depth of message tree."""

    max_children_count: int = 5
    """Maximum number of reply messages per tree node."""

    goal_tree_size: int = 15
    """Total number of messages to gather per tree."""

    num_reviews_initial_prompt: int = 3
    """Number of peer review checks to collect in INITIAL_PROMPT_REVIEW state."""

    num_reviews_reply: int = 3
    """Number of peer review checks to collect per reply (other than initial_prompt)."""

    p_full_labeling_review_prompt: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for initial prompts."""

    p_full_labeling_review_reply_assistant: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for assistant replies."""

    p_full_labeling_review_reply_prompter: float = 0.1
    """Probability of full text-labeling (instead of mandatory only) for prompter replies."""

    acceptance_threshold_initial_prompt: float = 0.6
    """Threshold for accepting an initial prompt."""

    acceptance_threshold_reply: float = 0.6
    """Threshold for accepting a reply."""

    num_required_rankings: int = 3
    """Number of rankings in which the message participated."""

    mandatory_labels_initial_prompt: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]
    """Mandatory labels in text-labeling tasks for initial prompts."""

    mandatory_labels_assistant_reply: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]
    """Mandatory labels in text-labeling tasks for assistant replies."""

    mandatory_labels_prompter_reply: Optional[list[protocol_schema.TextLabel]] = [protocol_schema.TextLabel.spam]
    """Mandatory labels in text-labeling tasks for prompter replies."""


class Settings(BaseSettings):
    PROJECT_NAME: str = "open-assistant backend"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    DATABASE_URI: Optional[PostgresDsn] = None

    RATE_LIMIT: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    DEBUG_ALLOW_ANY_API_KEY: bool = False
    DEBUG_SKIP_API_KEY_CHECK: bool = False
    DEBUG_USE_SEED_DATA: bool = False
    DEBUG_USE_SEED_DATA_PATH: Optional[FilePath] = (
        Path(__file__).parent.parent / "test_data/realistic/realistic_seed_data.json"
    )
    DEBUG_ALLOW_SELF_LABELING: bool = False  # allow users to label their own messages
    DEBUG_SKIP_EMBEDDING_COMPUTATION: bool = False
    DEBUG_SKIP_TOXICITY_CALCULATION: bool = False

    HUGGING_FACE_API_KEY: str = ""

    # For celery tasks queue
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    UPDATE_ALEMBIC: bool = True

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    tree_manager: Optional[TreeManagerConfiguration] = TreeManagerConfiguration()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"


settings = Settings()
