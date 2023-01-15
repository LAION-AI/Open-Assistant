from celery import Celery

app = Celery("batch", include=["batch.tasks.embedding", "batch.tasks.toxicity"])

app.config_from_object("batch.celeryconfig")

if __name__ == "__main__":
    app.start()
