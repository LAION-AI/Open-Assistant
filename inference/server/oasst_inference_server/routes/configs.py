import json

import fastapi
import pydantic
import requests
import yaml
from loguru import logger
from oasst_inference_server.settings import settings
from oasst_shared import model_configs
from oasst_shared.schemas import inference

# NOTE: Replace this with plugins that we will provide out of the box
DUMMY_PLUGINS = [
    inference.PluginEntry(
        url="http://192.168.0.35:8085/ai-plugin.json",
        enabled=False,
        trusted=True,
    ),
]

router = fastapi.APIRouter(
    prefix="/configs",
    tags=["configs"],
)


class ParameterConfig(pydantic.BaseModel):
    name: str
    description: str = ""
    sampling_parameters: inference.SamplingParameters


class ModelConfigInfo(pydantic.BaseModel):
    name: str
    description: str = ""
    parameter_configs: list[ParameterConfig] = []


DEFAULT_PARAMETER_CONFIGS = [
    ParameterConfig(
        name="k50",
        description="Top-k sampling with k=50",
        sampling_parameters=inference.SamplingParameters(
            top_k=50,
            top_p=0.95,
            temperature=0.9,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="nucleus9",
        description="Nucleus sampling with p=0.9",
        sampling_parameters=inference.SamplingParameters(
            top_p=0.9,
            temperature=0.8,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical2",
        description="Typical sampling with p=0.2",
        sampling_parameters=inference.SamplingParameters(
            temperature=0.8,
            typical_p=0.2,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="typical3",
        description="Typical sampling with p=0.3",
        sampling_parameters=inference.SamplingParameters(
            temperature=0.8,
            typical_p=0.3,
            repetition_penalty=1.2,
        ),
    ),
]


@router.get("/model_configs")
async def get_model_configs() -> list[ModelConfigInfo]:
    return [
        ModelConfigInfo(
            name=model_config_name,
            parameter_configs=DEFAULT_PARAMETER_CONFIGS,
        )
        for model_config_name in model_configs.MODEL_CONFIGS
        if (settings.allowed_model_config_names == "*" or model_config_name in settings.allowed_model_config_names_list)
    ]


@router.post("/plugin_config")
async def get_plugin_config(plugin: inference.PluginEntry) -> inference.PluginEntry | fastapi.HTTPException:
    plugin_config = None
    try:
        response = requests.get(plugin.url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return fastapi.HTTPException(status_code=404, detail="Plugin not found")

    config = {}
    try:
        content_type = response.headers.get("Content-Type")
        if "application/json" in content_type or plugin.url.endswith(".json"):
            config = json.loads(response.text)
        elif (
            "application/yaml" in content_type
            or "application/x-yaml" in content_type
            or plugin.url.endswith(".yaml")
            or plugin.url.endswith(".yml")
        ):
            config = yaml.safe_load(response.text)
        else:
            raise Exception(f"Unsupported content type: {content_type}. Only JSON and YAML are supported.")

        plugin_config = inference.PluginConfig(**config)
    except Exception as e:
        return fastapi.HTTPException(status_code=404, detail="Failed to parse plugin config, error: " + str(e))

    return inference.PluginEntry(url=plugin.url, enabled=plugin.enabled, plugin_config=plugin_config)


@router.get("/builtin_plugins")
async def get_builtin_plugins() -> list[inference.PluginEntry] | fastapi.HTTPException:
    plugins = []

    for plugin in DUMMY_PLUGINS:
        try:
            response = requests.get(plugin.url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.warning(f"Failed to fetch plugin config from {plugin.url}")
            continue

        try:
            plugin_config = inference.PluginConfig(**response.json())
        except ValueError:
            logger.warning(f"Failed to parse plugin config from {plugin.url}")
            continue

        final_plugin: inference.PluginEntry = inference.PluginEntry(
            url=plugin.url,
            enabled=plugin.enabled,
            trusted=plugin.trusted,
            plugin_config=plugin_config,
        )
        plugins.append(final_plugin)

    return plugins
