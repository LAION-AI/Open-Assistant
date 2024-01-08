### Prerequisites

- `model_training` and `flask`, `flask_wtf`, `flask_bootstrap` must be
  installed, see requirements.txt
- in order to make use of locally cached datasets define `cache_dir` in `app.py`
  as the path to the cached datasets
- datasets that can't be found locally will be loaded from huggingface

#### Starting the server

If you have `make` installed, just use `make run` or `make debug` (for
development on the server) Otherwise use `flask run` (with an active python
environment that has all dependencies listed in `requirements.txt`)
