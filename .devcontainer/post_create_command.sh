#!/bin/bash

# Run both backend-dev and frontend-dev post_create scripts

./.devcontainer/backend-dev/post_create_command.sh
./.devcontainer/frontend-dev/post_create_command.sh

# run yarn install in docs folder
cd docs
yarn install
cd ..
