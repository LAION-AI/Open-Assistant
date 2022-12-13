FROM python:3.10-slim-bullseye
RUN mkdir /app
ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app
CMD ["python", "bot.py"]