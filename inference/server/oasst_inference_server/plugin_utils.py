import asyncio
import json

import aiohttp
import yaml
from aiohttp.client_exceptions import ClientConnectorError, ServerTimeoutError
from fastapi import HTTPException
from loguru import logger
from oasst_shared.schemas import inference


async def attempt_fetch_plugin(session: aiohttp.ClientSession, url: str, timeout: float = 5.0):
    """Attempt to fetch a plugin specification from the given URL once."""
    async with session.get(url, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type")

        if response.status == 404:
            raise HTTPException(status_code=404, detail="Plugin not found")
        if response.status != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch plugin")

        if "application/json" in content_type or "text/json" in content_type or url.endswith(".json"):
            if "text/json" in content_type:
                logger.warning(f"Plugin {url} is using text/json as its content type. This is not recommended.")
                config = json.loads(await response.text())
            else:
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


async def fetch_plugin(url: str, retries: int = 3, timeout: float = 5.0) -> inference.PluginConfig:
    """Fetch a plugin specification from the given URL, with retries using exponential backoff."""
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                plugin_config = await attempt_fetch_plugin(session, url, timeout=timeout)
                return plugin_config
            except (ClientConnectorError, ServerTimeoutError) as e:
                if attempt == retries - 1:
                    raise HTTPException(status_code=500, detail=f"Request failed after {retries} retries: {e}")
                await asyncio.sleep(2**attempt)  # exponential backoff
            except aiohttp.ClientError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    raise HTTPException(status_code=500, detail="Failed to fetch plugin")
