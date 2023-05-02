import asyncio

import aiohttp
import fastapi
import pydantic
import yaml
from aiohttp.client_exceptions import ClientConnectorError, ServerTimeoutError
from fastapi import HTTPException
from loguru import logger
from oasst_inference_server.settings import settings
from oasst_shared import model_configs
from oasst_shared.schemas import inference

# NOTE: Populate this with plugins that we will provide out of the box
OA_PLUGINS = []

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
            temperature=0.75,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="k50-Creative",
        description="Top-k sampling with k=50, higher temperature",
        sampling_parameters=inference.SamplingParameters(
            top_k=50,
            top_p=0.95,
            temperature=0.85,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="k50-Precise",
        description="Top-k sampling with k=50, low temperature",
        sampling_parameters=inference.SamplingParameters(
            top_k=50,
            top_p=0.95,
            temperature=0.1,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="k50-Original",
        description="Top-k sampling with k=50, highest temperature",
        sampling_parameters=inference.SamplingParameters(
            top_k=50,
            top_p=0.95,
            temperature=0.9,
            repetition_penalty=1.2,
        ),
    ),
    ParameterConfig(
        name="k50-Plugins",
        description="Top-k sampling with k=50 and temperature=0.35",
        sampling_parameters=inference.SamplingParameters(
            max_new_tokens=1024,
            temperature=0.35,
            top_k=50,
            repetition_penalty=(1 / 0.90),
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


async def fetch_plugin(url: str, retries: int = 3, timeout: float = 5.0) -> inference.PluginConfig:
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=timeout) as response:
                    content_type = response.headers.get("Content-Type")

                    if response.status == 200:
                        if "application/json" in content_type or url.endswith(".json"):
                            config = await response.json()
                        elif (
                            "application/yaml" in content_type
                            or "application/x-yaml" in content_type
                            or url.endswith(".yaml")
                            or url.endswith(".yml")
                        ):
                            config = yaml.safe_load(await response.text())
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Unsupported content type: {content_type}. Only JSON and YAML are supported.",
                            )

                        return inference.PluginConfig(**config)
                    elif response.status == 404:
                        raise HTTPException(status_code=404, detail="Plugin not found")
                    else:
                        raise HTTPException(status_code=response.status, detail="Unexpected status code")
            except (ClientConnectorError, ServerTimeoutError) as e:
                if attempt == retries - 1:  # last attempt
                    raise HTTPException(status_code=500, detail=f"Request failed after {retries} retries: {e}")
                await asyncio.sleep(2**attempt)  # exponential backoff

            except aiohttp.ClientError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    raise HTTPException(status_code=500, detail="Failed to fetch plugin")


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
async def get_plugin_config(plugin: inference.PluginEntry) -> inference.PluginEntry:
    try:
        plugin_config = await fetch_plugin(plugin.url)
    except HTTPException as e:
        logger.warning(f"Failed to fetch plugin config from {plugin.url}: {e.detail}")
        raise fastapi.HTTPException(status_code=e.status_code, detail=e.detail)

    return inference.PluginEntry(url=plugin.url, enabled=plugin.enabled, plugin_config=plugin_config)


@router.get("/builtin_plugins")
async def get_builtin_plugins() -> list[inference.PluginEntry]:
    plugins = []

    for plugin in OA_PLUGINS:
        try:
            plugin_config = await fetch_plugin(plugin.url)
        except HTTPException as e:
            logger.warning(f"Failed to fetch plugin config from {plugin.url}: {e.detail}")
            continue

        final_plugin: inference.PluginEntry = inference.PluginEntry(
            url=plugin.url,
            enabled=plugin.enabled,
            trusted=plugin.trusted,
            plugin_config=plugin_config,
        )
        plugins.append(final_plugin)

    return plugins
