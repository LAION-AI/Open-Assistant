#!/bin/bash

gunicorn_workers=${GUNICORN_WORKERS:-1}

# if 1 worker, stay with uvicorn
if [ $gunicorn_workers -eq 1 ]; then
    unset PROMETHEUS_MULTIPROC_DIR
    uvicorn main:app --host 0.0.0.0 --port "$PORT"
else
    if [ -d "${PROMETHEUS_MULTIPROC_DIR}" ]; then rm -rf "${PROMETHEUS_MULTIPROC_DIR}"; fi
    mkdir -p "${PROMETHEUS_MULTIPROC_DIR}"
    port=${PORT:-8080}
    gunicorn main:app --workers $gunicorn_workers --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$port
fi
