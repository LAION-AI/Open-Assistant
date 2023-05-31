from oasst_inference_server.plugins.gale_pleaser.main import app as gale_pleaser

# dict of registered plugins
# The key defines a plugin's path which will be appended to the configured PLUGINS_PATH_PREFIX.
plugin_apps = {"/gale_pleaser": gale_pleaser}
