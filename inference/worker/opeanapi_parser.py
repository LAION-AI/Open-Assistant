import json

import requests
import yaml
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
        return plugin_dict
    except (requests.RequestException, ValueError) as e:
        print(f"Error downloading or parsing Plugin config: {e}")
        return None


# TODO: Extract endpoints from this function to separate one!
# also get rid of endpoints from PluginConfig class
def prepare_plugin_for_llm(plugin_url: str) -> inference.PluginConfig | None:
    plugin_config = get_plugin_config(plugin_url)
    if not plugin_config:
        return None

    openapi_dict = fetch_openapi_spec(plugin_config["api"]["url"])
    if not openapi_dict:
        return None

    endpoints = []

    base_url = ""
    if "servers" in openapi_dict:
        base_url = openapi_dict["servers"][0]["url"]

    paths = openapi_dict["paths"]

    for path, methods in paths.items():
        for method, details in methods.items():
            endpoint_data = {
                "type": method,
                "summary": details.get("summary", ""),
                "operation_id": details.get("operationId", ""),
                "url": f"{base_url}{path}"
                if base_url
                else plugin_config["api"]["url"].replace("/openapi.json", "") + path,
                "path": path,
                "params": [
                    inference.PluginOpenAPIParameter(
                        name=param["name"],
                        in_=param["in"],
                        description=param.get("description", ""),
                        required=param["required"],
                        schema_=param["schema"],
                    )
                    for param in details.get("parameters", [])
                ],
            }

            if "tags" in details:
                tag_name = details["tags"][0]
                endpoint_data["tag"] = tag_name

            endpoint = inference.PluginOpenAPIEndpoint(**endpoint_data)
            endpoints.append(endpoint)

            plugin_config["endpoints"] = endpoints
    return plugin_config
