# devcontainer

## example usage

Below are some example use cases you might want to run from within the
devcontainer (either
[within VSCode locally](https://code.visualstudio.com/docs/devcontainers/create-dev-container#_create-a-devcontainerjson-file)
or in your browser via
[GitHub Codespaces](https://github.com/features/codespaces)).

**Note**: If you want to chose a specific .devcontainer within GitHub codespaces
select "New with options" and you will be able to select any of the pre-defined
devcontainers in this repo.

### Run pre-commit

```bash
# run pre-commit
pre-commit run --all-files
```

A successful run should look something like this:

```
@andrewm4894 ➜ /workspaces/Open-Assistant (devcontainer-improvements) $ pre-commit run --all-files
[INFO] Initializing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Initializing environment for https://github.com/psf/black.
[INFO] Initializing environment for https://github.com/psf/black:.[jupyter].
[INFO] Initializing environment for https://github.com/pycqa/flake8.
[INFO] Initializing environment for https://github.com/pycqa/isort.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-prettier.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-prettier:prettier@2.7.1.
[INFO] Initializing environment for local.
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/psf/black.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/pycqa/flake8.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/pycqa/isort.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/pre-commit/mirrors-prettier.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for local.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
trim trailing whitespace.................................................Passed
check python ast.........................................................Passed
check yaml...............................................................Passed
check json...............................................................Passed
check for case conflicts.................................................Passed
detect private key.......................................................Passed
fix python encoding pragma...............................................Passed
forbid submodules....................................(no files to check)Skipped
mixed line ending........................................................Passed
fix requirements.txt.....................................................Passed
check that executables have shebangs.....................................Passed
check that scripts with shebangs are executable..........................Passed
check BOM - deprecated: use fix-byte-order-marker........................Passed
check for broken symlinks............................(no files to check)Skipped
check for merge conflicts................................................Passed
check for added large files..............................................Passed
fix end of files.........................................................Passed
black-jupyter............................................................Passed
flake8...................................................................Passed
isort....................................................................Passed
prettier.................................................................Passed
Lint website.............................................................Passed
```

### Docker compose

```bash
# build the image
docker compose up --build
```

You should see some docker containers being pulled and activated.

Once you see a line like:

```
open-assistant-web-1 | Listening on port 3000 url: http://localhost:3000
```

you should be able to access that port like below:

<img width="640" alt="image" src="https://user-images.githubusercontent.com/2178292/210395676-e9c2aab5-cb54-4ae6-b1eb-ac929fd73607.png">

this port can then be forwarded to a browser tab like below:

<img width="640" alt="image" src="https://user-images.githubusercontent.com/2178292/210396207-1b2e259f-4d5d-475d-b225-91e2bd004071.png">
