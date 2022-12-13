# Open-Chat-GPT REST Backend

## REST Server Configuration

Please either use environment variables or create a `.env` file in the backend root directory (in which this readme file is located) to specify the `DATABASE_URI`.

Example contents of a `.env` file for the backend:

```
DATABASE_URI="postgresql://<username>:<password>@<host>/<database_name>"
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080", "https://localhost", "https://localhost:4200", "https://localhost:3000", "https://localhost:8080", "http://dev.ocgpt.laion.ai", "https://stag.ocgpt.laion.ai", "https://ocgpt.laion.ai"]

```

## Running the REST Server locally for development

First, install the requirements in `requirements.txt`.
Then, run two terminals (note the working directory for each):

- Terminal 1, to go `backend/scripts` and run `docker-compose up`. This will start postgres.
- Terminal 2, to go `backend` and run `scripts/run-local.sh`. This will start the REST server.
