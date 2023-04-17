#!/bin/bash

gunicorn_workers=${GUNICORN_WORKERS:-1}

# if 1 worker, stay with uvicorn
if [ $gunicorn_workers -eq 1 ]; then
    uvicorn main:app --host 0.0.0.0 --port "$PORT"
else
    port=${PORT:-8080}
    gunicorn main:app --workers $gunicorn_workers --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$port
fi
