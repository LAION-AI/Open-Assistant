# Open-Chat-GPT REST Backend

## Alembic database init

~~Please edit `alembic.ini` and specify your database URI in the parameter `sqlalchemy.url = postgresql://<username>:<password>@<host>/<database_name>`.~~

set the DATABASE_URI environment variable to the database URI, alembic will upgrade automatically on startup.

## REST Server Configuration

Please either use environment variables or create a `.env` file in the backend root directory (in which this readme file is located) to specify the `DATABASE_URI`.

Example contents of a `.env` file for the backend:

```
DATABASE_URI="postgresql://<username>:<password>@<host>/<database_name>"
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080", "https://localhost", "https://localhost:4200", "https://localhost:3000", "https://localhost:8080", "http://dev.ocgpt.laion.ai", "https://stag.ocgpt.laion.ai", "https://ocgpt.laion.ai"]

```

## Running the REST Server locally for development

Run two terminals (note the working directory for each):

- Terminal 1, to go `backend/scripts` and run `docker-compose up`. This will start postgres.
- Terminal 2, to go `backend` and run `scripts/run-local.sh`. This will start the REST server.
