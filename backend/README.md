<a href="https://github-com.translate.goog/LAION-AI/Open-Assistant/blob/main/backend/README.md?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp">![Translate](https://img.shields.io/badge/Translate-blue)</a>

# Open-Assistant REST Backend

## Backend Development Setup

### Local Database

In root directory, run
`docker compose --profile backend-dev up --build --attach-dependencies` to start
a database. The default settings are already configured to connect to the
database at `localhost:5432`. (See
[FAQ](https://projects.laion.ai/Open-Assistant/docs/faq#enable-dockers-buildkit-backend)
if you face any docker problems).

> **Note:** when running on MacOS with an M1 chip you have to use:
> `DB_PLATFORM=linux/x86_64 docker compose ...`

Python 3.10 is required. It is recommended to use `pyenv` which will recognise
the `.python-version` in the project root directory.

### Python Packages

Next, to install all requirements, You can run

1. `pip install -r backend/requirements.txt`
2. `pip install -e ./oasst-shared/.`
3. `pip install -e ./oasst-data/.`
4. `./scripts/backend-development/run-local.sh` to run the backend. This will
   start the backend server at `http://localhost:8080`.

## REST Server Configuration

- Generate a new environment variable file `.env` by coping the content of the
  [.env.example](.env.example) file.

- Update the values of the environment variables in the `.env` file by setting
  the DATABASE_URI to you local database URI.

- Update the rest of the environment variables according to your needs.

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

## API Documentation

Once you have successfully started the backend server, you can access the
default api docs at `localhost:8080/docs`. If you need to update the exported
openapi.json in the docs/ folder you can run below command to `wget` them from
the relevant local fastapi endpoint. This will enable anyone to just see API
docs via something like
[Swagger.io](https://editor.swagger.io/?url=https://raw.githubusercontent.com/LAION-AI/Open-Assistant/main/docs/docs/api/openapi.json)
without having to actually set up and run a development backend.

```bash
# save openapi.json to docs/docs/api/
wget localhost:8080/api/v1/openapi.json -O docs/docs/api/backend-openapi.json
```

Note: The api docs should be automatically updated by the
`test-api-contract.yaml` workflow. (TODO)

## Running Celery Worker(s) for API and periodic tasks

Celery workers are used for Huggingface API calls like toxicity and feature
extraction. Celery Beat along with worker is used for periodic tasks like user
streak update

To run APIs locally

- update HUGGING_FACE_API_KEY in backend/oasst_backend/config.py with the
  correct API_KEY
- `export DEBUG_SKIP_TOXICITY_CALCULATION=False` and
  `export DEBUG_SKIP_EMBEDDING_COMPUTATION=False`in
  `scripts/backend-development/run-local.sh`
- run start_worker.sh in backend dir
- to see logs , use `tail -f celery.log` and `tail -f celery.beat.log`

In CI

- set `DEBUG_SKIP_TOXICITY_CALCULATION=False` and
  `DEBUG_SKIP_EMBEDDING_COMPUTATION=False` in docker-compose.yaml
- Two Docker instances are created. One for Beat and other for the worker
- Logs can be viewed like other docker instances

## Exporting Data

When you have collected some data in the backend database, you can export it
using the `export.py` script provided in this directory. This can be run from
the command line using an Python environment with the same requirements as the
backend itself. The script connects to the database in the same manner as the
backend and therefore uses the same environmental variables.

A simple usage of the script, to export all English trees which successfully
passed the review process, may look like:

```bash
python export.py --lang en --export-file output.jsonl
```

There are many options available to filter the data which can be found in the
help message of the script: `python export.py --help`.

**Why isn't my export working?**

Common issues include (WIP):

- The messages have not passed the review process yet so the trees are not ready
  for export. This can be solved by including the `--include-spam` flag.
