# Open-Assistant REST Backend

## Backend Development Setup

In root directory, run
`docker compose up backend-dev --build --attach-dependencies` to start a
database. The default settings are already configured to connect to the database
at `localhost:5432`.

Make sure you have all requirements installed. You can do this by running
`pip install -r requirements.txt` inside the `backend` folder and
`pip install -e .` inside the `oasst-shared` folder. Then, run the backend using
the `run-local.sh` script inside the `scripts` folder. This will start the
backend server at `http://localhost:8080`.

## REST Server Configuration

Please either use environment variables or create a `.env` file in the backend
root directory (in which this readme file is located) to specify the
`DATABASE_URI`.

Example contents of a `.env` file for the backend:

```
DATABASE_URI="postgresql://<username>:<password>@<host>/<database_name>"
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080", "https://localhost", "https://localhost:4200", "https://localhost:3000", "https://localhost:8080", "http://dev.oasst.laion.ai", "https://stag.oasst.laion.ai", "https://oasst.laion.ai"]
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Running the REST Server locally for development

Have a look into the main `README.md` file for more information on how to set up
the backend for development. Use the scripts within the
scripts/backend-development folder to run the BE API locally.

## Alembic

To create an Alembic database migration script after sql-models were modified
run `alembic revision --autogenerate -m "..."` ("..." is what you did) in the
`/backend` directory. Then edit the newly created file. See
[here](https://alembic.sqlalchemy.org/en/latest/tutorial.html) for more
information.
