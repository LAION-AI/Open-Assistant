from oasst_backend.batch.broker.celery import app


@app.task
def batch_embedding():
    return 1
