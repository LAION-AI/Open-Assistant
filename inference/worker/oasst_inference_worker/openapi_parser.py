import json
from urllib.parse import urlsplit

import requests
import yaml
from loguru import logger
from oasst_shared.schemas import inference


def fetch_openapi_spec(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from URL: {url}. Status code: {response.status_code}")

    content_type = response.headers.get("Content-Type")

    if "application/json" in content_type or url.endswith(".json"):
        return json.loads(response.text)
    elif (
        "application/yaml" in content_type
        or "application/x-yaml" in content_type
        or url.endswith(".yaml")
        or url.endswith(".yml")
    ):
        return yaml.safe_load(response.text)
    else:
        raise Exception(f"Unsupported content type: {content_type}. Only JSON and YAML are supported.")


def get_plugin_config(url: str) -> inference.PluginConfig | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        plugin_dict = response.json()
        logger.info(f"Plugin config downloaded {plugin_dict}")
        plugin_config = inference.PluginConfig.parse_obj(plugin_dict)
        return plugin_config
    except (requests.RequestException, ValueError) as e:
        logger.warning(f"Error downloading or parsing Plugin config: {e}")
        return None


def resolve_schema_reference(ref: str, openapi_dict: dict):
    if not ref.startswith("#/"):
        raise ValueError(f"Invalid reference format: {ref}")

    components = ref.split("/")
    schema = openapi_dict
    for component in components[1:]:
        if component not in schema:
            raise ValueError(f"Reference component not found: {component}")
        schema = schema[component]

    return schema


def parse_plugin_endpoint(
    api_url: str,
    method: str,
    details: dict,
    base_url: str,
    path: str,
    openapi_dict: dict,
) -> inference.PluginOpenAPIEndpoint:
    """
    Parse details of a single plugin endpoint from OpenAPI spec.

    Args:
        api_url: URL of the plugin API.
        method: HTTP method of the endpoint.
        details: Details of the endpoint from OpenAPI spec.
        base_url: Base URL of the plugin.
        path: Path of the endpoint.
        openapi_dict: Full OpenAPI spec of the plugin.
    """
    split_result = urlsplit(api_url)
    backup_url = f"{split_result.scheme}://{split_result.netloc}"
    params_list = []
    parameters = details.get("parameters", [])
    if parameters is not None:
        for param in parameters:
            schema = None
            if "$ref" in param["schema"]:
                schema = resolve_schema_reference(param["schema"]["$ref"], openapi_dict)

            params_list.append(
                inference.PluginOpenAPIParameter(
                    name=param.get("name", ""),
                    in_=param.get("in", "query"),
                    description=param.get("description", ""),
                    required=param.get("required", False),
                    schema_=schema,
                )
            )
    # Check if the method is POST and extract request body schema
    payload = None
    if "requestBody" in details:
        content = details["requestBody"].get("content", {})
        for media_type, media_schema in content.items():
            if media_type == "application/json":
                if "$ref" in media_schema["schema"]:
                    payload = resolve_schema_reference(media_schema["schema"]["$ref"], openapi_dict)
                else:
                    payload = media_schema["schema"]

    endpoint_data = {
        "type": method,
        "summary": details.get("summary", ""),
        "operation_id": details.get("operationId", ""),
        "url": f"{base_url}{path}" if base_url is not None else f"{backup_url}{path}",
        "path": path,
        "params": params_list,
        "payload": payload,
    }

    if "tags" in details:
        tag_name = details["tags"][0]
        endpoint_data["tag"] = tag_name

    endpoint = inference.PluginOpenAPIEndpoint(**endpoint_data)
    return endpoint


def get_plugin_endpoints(api_url: str, openapi_dict: dict) -> list[inference.PluginOpenAPIEndpoint]:
    endpoints = []
    base_url = openapi_dict.get("servers", [{}])[0].get("url")

    if base_url is not None:
        parsed_link = urlsplit(api_url)
        base_url = (
            f"{parsed_link.scheme}://{parsed_link.netloc}{base_url}" if not urlsplit(base_url).scheme else base_url
        )

    for path, methods in openapi_dict.get("paths", {}).items():
        for method, details in methods.items():
            endpoints.append(parse_plugin_endpoint(api_url, method, details, base_url, path, openapi_dict))

    return endpoints


def prepare_plugin_for_llm(plugin_url: str) -> inference.PluginConfig | None:
    plugin_config = get_plugin_config(plugin_url)

    if not plugin_config:
        return None

    try:
        parsed_url = urlsplit(plugin_config.api.url)
        if parsed_url.scheme == "":
            api_url = urlsplit(plugin_url)._replace(path=parsed_url.path).geturl()
        else:
            api_url = plugin_config.api.url

        openapi_dict = fetch_openapi_spec(api_url)
        plugin_config.endpoints = get_plugin_endpoints(api_url, openapi_dict)
        return plugin_config

    except Exception:
        logger.debug(f"Plugin preparation error: {plugin_url}")
        return None
