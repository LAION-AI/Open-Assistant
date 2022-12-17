FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PORT 8080

COPY ./alembic.ini /alembic.ini
COPY ./alembic /alembic
COPY ./app /app
