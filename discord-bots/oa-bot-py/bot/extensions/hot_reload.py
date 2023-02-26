"""Hot reload plugin."""
from glob import glob

import hikari
import lightbulb
from loguru import logger

plugin = lightbulb.Plugin(
    "HotReloadPlugin",
)
plugin.add_checks(lightbulb.owner_only)

EXTENSIONS_FOLDER = "bot/extensions"


def _get_extensions() -> list[str]:
    # Recursively get all the .py files in the extensions directory not starting with an `_`.
    exts = glob("bot/extensions/**/[!_]*.py", recursive=True)
    # Turn the path into a plugin path ("path/to/extension.py" -> "path.to.extension")
    return [ext.replace("/", ".").replace("\\", ".").replace(".py", "") for ext in exts]


async def _plugin_autocomplete(option: hikari.CommandInteractionOption, _: hikari.AutocompleteInteraction) -> list[str]:
    # Check that the option is a string.
    if not isinstance(option.value, str):
        raise TypeError(f"`option.value` must be of type `str`, it is currently a `{type(option.value)}`")

    exts = _get_extensions()
    return [ext for ext in exts if option.value in ext]


@plugin.command
@lightbulb.option(
    "plugin",
    "The plugin to reload. Leave empty to reload all plugins.",
    autocomplete=_plugin_autocomplete,
    required=False,
    default=None,
)
@lightbulb.command("reload", "Reload a plugin", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def reload(ctx: lightbulb.SlashContext):
    """Reload a plugin or all plugins."""
    # If the plugin option is None, reload all plugins.
    if ctx.options.plugin is None:
        ctx.bot.reload_extensions(*_get_extensions())
        await ctx.respond("Reloaded all plugins.")
        logger.info("Reloaded all plugins.")
    # Otherwise, reload the specified plugin.
    else:
        ctx.bot.reload_extensions(ctx.options.plugin)
        await ctx.respond(f"Reloaded `{ctx.options.plugin}`.")
        logger.info(f"Reloaded `{ctx.options.plugin}`.")


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
