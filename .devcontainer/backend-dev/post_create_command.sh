# ensure pre-commit is installed
pre-commit install

# create python virtual environment
python3 -m venv .venv

# install python dependencies in /backend
cd backend
pip install -r requirements.txt
cd ..

# install code in editable mode in /oasst-shared
cd oasst-shared
pip install -e .
cd ..

# docker compose up for backend-dev
docker compose up backend-dev --build --attach-dependencies -d

# run run-local.sh script
cd scripts/backend-development/
bash run-local.sh

# save openapi.json to docs/docs/api
wget localhost:8080/api/v1/openapi.json -O docs/docs/api/openapi.json
