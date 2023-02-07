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
docker compose up backend-dev --build --attach-dependencies

# note: commented out for now, you probably want to manually run this part once in the devcontainer
# run run-local.sh script
# cd scripts/backend-development/
# bash run-local.sh
