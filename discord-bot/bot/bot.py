"""Bot logic."""
from datetime import datetime

import aiosqlite
import hikari
import lightbulb
import miru
from bot.settings import Settings
from bot.utils import mention
from oasst_shared.api_client import OasstApiClient

settings = Settings()

# TODO: Revisit cache settings
bot = lightbulb.BotApp(
    token=settings.bot_token,
    logs="DEBUG",
    prefix=settings.prefix,
    default_enabled_guilds=settings.declare_global_commands,
    owner_ids=settings.owner_ids,
    intents=hikari.Intents.ALL,
    help_class=None,
)


@bot.listen()
async def on_starting(event: hikari.StartingEvent):
    """Setup."""
    miru.install(bot)  # component handler
    bot.load_extensions_from("./bot/extensions")  # load extensions

    # Database setup
    bot.d.db = await aiosqlite.connect("./bot/db/database.db")
    await bot.d.db.executescript(open("./bot/db/schema.sql").read())
    await bot.d.db.commit()

    # OASST API setup
    bot.d.oasst_api = OasstApiClient(settings.oasst_api_url, settings.oasst_api_key)

    # A `dict[hikari.Message | None, UUID | None]]` that maps user IDs to (task msg ID, task UUIDs).
    # Either both are `None` or both are not `None`.
    # If both are `None`, the user is not currently selecting a task.
    # TODO: Grow this on startup so we don't have to re-allocate memory every time it needs to grow
    bot.d.currently_working = {}


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent):
    """Cleanup."""
    await bot.d.db.close()
    await bot.d.oasst_api.close()


async def _send_error_embed(
    content: str, exception: lightbulb.errors.LightbulbError | BaseException, ctx: lightbulb.Context
) -> None:
    ctx.command
    embed = hikari.Embed(
        title=f"`{exception.__class__.__name__}` Error{f' in `/{ctx.command.name}`' if ctx.command else '' }",
        description=content,
        color=0xFF0000,
        timestamp=datetime.now().astimezone(),
    ).set_author(name=ctx.author.username, url=str(ctx.author.avatar_url))

    await ctx.respond(embed=embed)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    """Error handler for the bot."""
    # Unwrap the exception to get the original cause
    exc = event.exception.__cause__ or event.exception
    ctx = event.context
    if not ctx.bot.rest.is_alive:
        return

    if isinstance(event.exception, lightbulb.CommandInvocationError):
        if not event.context.command:
            await _send_error_embed("Something went wrong", exc, ctx)
        else:
            await _send_error_embed(
                f"Something went wrong during invocation of command `{event.context.command.name}`.", exc, ctx
            )

        raise event.exception

    # Not an owner
    if isinstance(exc, lightbulb.NotOwner):
        await _send_error_embed("You are not the owner of this bot.", exc, ctx)
    # Command is on cooldown
    elif isinstance(exc, lightbulb.CommandIsOnCooldown):
        await _send_error_embed(f"This command is on cooldown. Retry in `{exc.retry_after:.2f}` seconds.", exc, ctx)
    # Missing permissions
    elif isinstance(exc, lightbulb.errors.MissingRequiredPermission):
        await _send_error_embed(
            f"You do not have permission to use this command. Missing permissions: {exc.missing_perms}", exc, ctx
        )
    # Missing roles
    elif isinstance(exc, lightbulb.errors.MissingRequiredRole):
        assert event.context.guild_id is not None  # Roles only exist in guilds
        await _send_error_embed(
            f"You do not have the correct role to use this command. Missing role(s): {[mention(r, 'role') for r in exc.missing_roles]}",
            exc,
            ctx,
        )
    # Only a guild command
    elif isinstance(exc, lightbulb.errors.OnlyInGuild):
        await _send_error_embed("This command can only be run in servers.", exc, ctx)
    # Only a DM command
    elif isinstance(exc, lightbulb.errors.OnlyInDM):
        await _send_error_embed("This command can only be run in DMs.", exc, ctx)
    # Not enough arguments
    elif isinstance(exc, lightbulb.errors.NotEnoughArguments):
        await _send_error_embed(
            f"Not enough arguments were supplied to the command. {[opt.name for opt in exc.missing_options]}", exc, ctx
        )
    # Bot missing permission
    elif isinstance(exc, lightbulb.errors.BotMissingRequiredPermission):
        await _send_error_embed(
            f"The bot does not have the correct permission(s) to execute this command. Missing permissions: {exc.missing_perms}",
            exc,
            ctx,
        )
    elif isinstance(exc, lightbulb.errors.MissingRequiredAttachment):
        await _send_error_embed("Not enough attachments were supplied to this command.", exc, ctx)
    elif isinstance(exc, lightbulb.errors.CommandNotFound):
        await ctx.respond(f"`/{exc.invoked_with}` is not a valid command. Use `/help` to see a list of commands.")
    else:
        raise exc
