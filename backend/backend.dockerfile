FROM python:3.10

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

COPY ./alembic.ini /backend/alembic.ini
COPY ./alembic /backend/alembic
COPY ./app /backend/app

ENV PYTHONPATH=/backend/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
