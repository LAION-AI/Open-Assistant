from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from oasst_shared.schemas.protocol import TextLabel
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, FilePath, PostgresDsn, validator


class TreeManagerConfiguration(BaseModel):
    """TreeManager configuration settings"""

    max_active_trees: int = 10
    """Maximum number of concurrently active message trees in the database.
    No new initial prompt tasks are handed out to users if this
    number is reached."""

    max_tree_depth: int = 6
    """Maximum depth of message tree."""

    max_children_count: int = 3
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

    p_activate_backlog_tree: float = 0.8
    """Probability to activate a message tree in BACKLOG_RANKING state when another tree enters
    a terminal state. Use this settting to control ratio of initial prompts and backlog tree
    activations."""

    min_active_rankings_per_lang: int = 2
    """When the number of active ranking tasks is below this value when a tree enters a terminal
    state an available trees in BACKLOG_RANKING will be actived (i.e. enters the RANKING state)."""

    labels_initial_prompt: list[TextLabel] = [
        TextLabel.spam,
        TextLabel.quality,
        TextLabel.helpfulness,
        TextLabel.creativity,
        TextLabel.humor,
        TextLabel.toxicity,
        TextLabel.violence,
        TextLabel.not_appropriate,
        TextLabel.pii,
        TextLabel.hate_speech,
        TextLabel.sexual_content,
    ]

    labels_assistant_reply: list[TextLabel] = [
        TextLabel.spam,
        TextLabel.fails_task,
        TextLabel.quality,
        TextLabel.helpfulness,
        TextLabel.creativity,
        TextLabel.humor,
        TextLabel.toxicity,
        TextLabel.violence,
        TextLabel.not_appropriate,
        TextLabel.pii,
        TextLabel.hate_speech,
        TextLabel.sexual_content,
    ]

    labels_prompter_reply: list[TextLabel] = [
        TextLabel.spam,
        TextLabel.quality,
        TextLabel.helpfulness,
        TextLabel.humor,
        TextLabel.creativity,
        TextLabel.toxicity,
        TextLabel.violence,
        TextLabel.not_appropriate,
        TextLabel.pii,
        TextLabel.hate_speech,
        TextLabel.sexual_content,
    ]

    mandatory_labels_initial_prompt: Optional[list[TextLabel]] = [TextLabel.spam]
    """Mandatory labels in text-labeling tasks for initial prompts."""

    mandatory_labels_assistant_reply: Optional[list[TextLabel]] = [TextLabel.spam]
    """Mandatory labels in text-labeling tasks for assistant replies."""

    mandatory_labels_prompter_reply: Optional[list[TextLabel]] = [TextLabel.spam]
    """Mandatory labels in text-labeling tasks for prompter replies."""

    rank_prompter_replies: bool = False

    lonely_children_count: int = 2
    """Number of children below which parents are preferred during sampling for reply tasks."""

    p_lonely_child_extension: float = 0.8
    """Probability to select a parent with less than lonely_children_count children."""

    recent_tasks_span_sec: int = 3 * 60  # 3 min
    """Time in seconds of recent tasks to consider for exclusion during task selection."""


class Settings(BaseSettings):
    PROJECT_NAME: str = "open-assistant backend"
    API_V1_STR: str = "/api/v1"
    OFFICIAL_WEB_API_KEY: str = "1234"

    # Encryption fields for handling the web generated JSON Web Tokens.
    # These fields need to be shared with the web's auth settings in order to
    # correctly decrypt the web tokens.
    AUTH_INFO: bytes = b"NextAuth.js Generated Encryption Key"
    AUTH_SALT: bytes = b""
    AUTH_LENGTH: int = 32
    AUTH_SECRET: bytes = b"O/M2uIbGj+lDD2oyNa8ax4jEOJqCPJzO53UbWShmq98="
    AUTH_COOKIE_NAME: str = "next-auth.session-token"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    DATABASE_URI: Optional[PostgresDsn] = None
    DATABASE_MAX_TX_RETRY_COUNT: int = 3

    RATE_LIMIT: bool = True
    MESSAGE_SIZE_LIMIT: int = 2000
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    DEBUG_USE_SEED_DATA: bool = False
    DEBUG_USE_SEED_DATA_PATH: Optional[FilePath] = (
        Path(__file__).parent.parent / "test_data/realistic/realistic_seed_data.json"
    )
    DEBUG_ALLOW_SELF_LABELING: bool = False  # allow users to label their own messages
    DEBUG_ALLOW_DUPLICATE_TASKS: bool = False  # offer users tasks to which they already responded
    DEBUG_SKIP_EMBEDDING_COMPUTATION: bool = False
    DEBUG_SKIP_TOXICITY_CALCULATION: bool = False
    DEBUG_DATABASE_ECHO: bool = False

    DUPLICATE_MESSAGE_FILTER_WINDOW_MINUTES: int = 120

    HUGGING_FACE_API_KEY: str = ""

    ROOT_TOKENS: List[str] = ["1234"]  # supply a string that can be parsed to a json list

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

    USER_STATS_INTERVAL_DAY: int = 5  # minutes
    USER_STATS_INTERVAL_WEEK: int = 15  # minutes
    USER_STATS_INTERVAL_MONTH: int = 60  # minutes
    USER_STATS_INTERVAL_TOTAL: int = 240  # minutes

    @validator(
        "USER_STATS_INTERVAL_DAY",
        "USER_STATS_INTERVAL_WEEK",
        "USER_STATS_INTERVAL_MONTH",
        "USER_STATS_INTERVAL_TOTAL",
    )
    def validate_user_stats_intervals(cls, v: int):
        if v < 1:
            raise ValueError(v)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"


settings = Settings()
