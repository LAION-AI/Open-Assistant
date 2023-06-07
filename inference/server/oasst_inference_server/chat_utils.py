from oasst_inference_server.settings import settings
from oasst_shared import model_configs


def get_model_config(model_config_name: str) -> model_configs.ModelConfig:
    if settings.allowed_model_config_names != "*":
        if model_config_name not in settings.allowed_model_config_names_list:
            raise ValueError(f"Model {model_config_name} not in allowed models: {settings.allowed_model_config_names}")

    model_config = model_configs.MODEL_CONFIGS.get(model_config_name)
    if model_config is None:
        raise ValueError(
            f"Model {model_config_name} not found",
        )
    return model_config
