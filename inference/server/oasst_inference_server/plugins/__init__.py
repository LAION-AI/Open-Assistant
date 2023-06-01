from oasst_inference_server.plugins.gale_pleaser.main import app as gale_pleaser
from oasst_inference_server.plugins.gale_roaster.main import app as gale_roaster
from oasst_inference_server.plugins.web_retriever.main import app as web_retriever

# dict of registered plugins
# The key defines a plugin's path which will be appended to the configured PLUGINS_PATH_PREFIX.
plugin_apps = {
    "/gale_pleaser": gale_pleaser,
    "/gale_roaster": gale_roaster,
    "/web_retriever": web_retriever,
}
