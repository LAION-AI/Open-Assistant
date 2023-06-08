import os

from celery import Celery
from loguru import logger

"""
To run the worker run `celery run -A oasst_backend.celery_worker worker -l INFO`
in the parent directory of this file, add -B to embed the beat scheduler inside
the worker.
"""
app = Celery(
    "oasst_worker",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["oasst_backend.scheduled_tasks"],
)

logger.info(f"celery.conf.broker_url {app.conf.broker_url}, app.conf.result_backend{app.conf.result_backend}")

# see https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    "reset-user-streak": {
        "task": "periodic_user_streak_reset",
        "schedule": 60.0 * 60.0 * 4,  # in seconds, every 4h
    },
    "update-search-vectors": {
        "task": "update_search_vectors",
        "schedule": 60.0 * 20.0,
        "args": (1000,),  # (batch_size,)
    },
}
app.conf.timezone = "UTC"
