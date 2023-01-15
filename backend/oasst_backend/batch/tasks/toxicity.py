from oasst_backend.batch.broker.celery import app


@app.task
def batch_toxicity():
    return 1
