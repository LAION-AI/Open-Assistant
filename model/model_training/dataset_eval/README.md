### Prerequisites

- `model_training` and `flask`, `flask_wtf`, `flask_bootstrap` must be
  installed, see requirements.txt
- in order to make use of locally cached datasets define `cache_dir` in `app.py`
  as the path to the cached datasets
- datasets that can't be found locally will be loaded from huggingface
