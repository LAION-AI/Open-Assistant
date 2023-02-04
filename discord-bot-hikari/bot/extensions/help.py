"""Custom help command."""
import lightbulb
from bot.messages import help_message, tutorial_message
from bot.settings import Settings
from hikari.permissions import Permissions
from lightbulb.utils import permissions_for

plugin = lightbulb.Plugin("HelpPlugin")

settings = Settings()


@plugin.command
@lightbulb.command("help", "Help for the bot.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def help_command(ctx: lightbulb.Context) -> None:
    """Help for the bot."""
    can_manage_guild = False
    if ctx.guild_id:
        member = ctx.bot.cache.get_member(ctx.guild_id, ctx.author.id) or await ctx.bot.rest.fetch_member(
            ctx.guild_id, ctx.author.id
        )
        can_manage_guild = bool(permissions_for(member) & Permissions.MANAGE_GUILD)

    await ctx.respond(help_message(can_manage_guild, ctx.author.id in settings.owner_ids))


@plugin.command
@lightbulb.command("tutorial", "A tutorial for completing tasks.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def tutorial(ctx: lightbulb.Context) -> None:
    """Help for the bot."""
    await ctx.respond(tutorial_message(True, True))


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
