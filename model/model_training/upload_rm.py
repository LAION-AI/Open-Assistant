from huggingface_hub import HfApi
api = HfApi()

# Upload all the content from the local folder to your remote Space.
# By default, files are uploaded at the root of the repo
api.upload_folder(
    folder_path=".saved_models_rm",
    repo_id="toanbku/oa-rm-2.1-pythia-1.4b-df",
    repo_type="model",
)
