"""Custom help command."""
import lightbulb
from bot.messages import help_message
from bot.settings import Settings

plugin = lightbulb.Plugin("HelpPlugin")

settings = Settings()


@plugin.command
@lightbulb.command("help", "Help for the bot.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def help_command(ctx: lightbulb.Context) -> None:
    """Help for the bot."""
    await ctx.respond(help_message(True, True))


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
