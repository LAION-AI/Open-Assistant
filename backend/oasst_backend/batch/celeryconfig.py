from oasst_backend.config import settings

broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/London"
enable_utc = True

# Create the queues values
task_routes = [("tasks.toxicity.*", {"queue": "toxicity"}), ("tasks.embedding.*", {"queue": "embedding"})]
