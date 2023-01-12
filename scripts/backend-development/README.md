# Backend Development Setup

In root directory, run
`docker compose up backend-dev --build --attach-dependencies` to start a
database. The default settings are already configured to connect to the database
at `localhost:5432`.

Make sure you have all requirements installed. You can do this by running
`pip install -r requirements.txt` inside the `backend` folder and
`pip install -e .` inside the `oasst-shared` folder. Then, run the backend using
the `run-local.sh` script. This will start the backend server at
`http://localhost:8080`.
