# Open-Assistant REST Backend

## REST Server Configuration

Please either use environment variables or create a `.env` file in the backend
root directory (in which this readme file is located) to specify the
`DATABASE_URI`.

Example contents of a `.env` file for the backend:

```
DATABASE_URI="postgresql://<username>:<password>@<host>/<database_name>"
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080", "https://localhost", "https://localhost:4200", "https://localhost:3000", "https://localhost:8080", "http://dev.oasst.laion.ai", "https://stag.oasst.laion.ai", "https://oasst.laion.ai"]

```

## Running the REST Server locally for development

Have a look into the main `README.md` file for more information on how to set up
the backend for development.
