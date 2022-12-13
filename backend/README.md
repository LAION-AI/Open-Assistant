# Open-Chat-GPT REST Backend

## Almbeic database init

Please edit `alembic.ini` and specify your database uri in the parameter `sqlalchemy.url`.

## REST Server Configuration

Please either use environment variables or create a `.env` file in the backend root directory (in which this readme file is located) to specify the `DATABASE_URI`.

Example contents of a `.env` file for the backend:

```
DATABASE_URI="postgresql://<username>:<password>@<host>/<database_name>"
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080", "https://localhost", "https://localhost:4200", "https://localhost:3000", "https://localhost:8080", "http://dev.ocgpt.laion.ai", "https://stag.ocgpt.laion.ai", "https://ocgpt.laion.ai"]

```
