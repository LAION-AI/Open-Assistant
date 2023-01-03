"""Hot reload plugin."""
import typing as t
from datetime import datetime

import hikari
import lightbulb
import miru
from aiosqlite import Connection
from bot.db.schemas import GuildSettings
from loguru import logger

plugin = lightbulb.Plugin(
    "TextLabels",
)
plugin.add_checks(lightbulb.guild_only)  # Context menus are only enabled in guilds


DISCORD_GRAY = 0x2F3136


def clamp(num: float) -> float:
    """Clamp a number between 0 and 1."""
    return min(max(0.0, num), 1.0)


class LabelModal(miru.Modal):
    """Modal for submitting text labels."""

    def __init__(self, label: str, content: str, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)
        self.label = label
        self.original_content = content

        # Add the text of the message to the modal
        self.content = miru.TextInput(
            label="Text", style=hikari.TextInputStyle.PARAGRAPH, value=content, required=True, row=1
        )
        self.add_item(self.content)

    value = miru.TextInput(label="Value", placeholder="Enter a value between 0 and 1", required=True, row=2)

    async def callback(self, context: miru.ModalContext) -> None:
        val = float(self.value.value) if self.value.value else 0.0
        val = clamp(val)

        edited = self.content.value != self.original_content
        await context.respond(
            f"Sending {self.label}=`{val}` for `{self.content.value}` (edited={edited}) to the backend.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        logger.info(f"Sending {self.label}=`{val}` for `{self.content.value}` (edited={edited}) to the backend.")

        # Send a notification to the log channel
        assert context.guild_id is not None  # `guild_only` check
        conn: Connection = context.bot.d.db  # type: ignore
        guild_settings = await GuildSettings.from_db(conn, context.guild_id)

        if guild_settings is None or guild_settings.log_channel_id is None:
            logger.warning(f"No guild settings or log channel for guild {context.guild_id}")
            return

        embed = (
            hikari.Embed(
                title="Message Label",
                description=f"{context.author.mention} labeled a message as `{self.label}`.",
                timestamp=datetime.now().astimezone(),
                color=0x00FF00,
            )
            .set_author(name=context.author.username, icon=context.author.avatar_url)
            .add_field("Total Labeled Message", "0", inline=True)
            .add_field("Server Ranking", "0/0", inline=True)
            .add_field("Global Ranking", "0/0", inline=True)
        )
        channel = await context.bot.rest.fetch_channel(guild_settings.log_channel_id)
        assert isinstance(channel, hikari.TextableChannel)
        await channel.send(embed=embed)


class LabelSelect(miru.View):
    """Select menu for selecting a label.

    The current labels are:
    - contains toxic language
    - encourages illegal activity
    - good quality
    - bad quality
    - is spam
    """

    def __init__(self, content: str, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)
        self.content = content

    @miru.select(
        options=[
            hikari.SelectMenuOption(
                label="Toxic Language",
                value="toxic_language",
                description="The message contains toxic language.",
                is_default=False,
                emoji=None,
            ),
            hikari.SelectMenuOption(
                label="Illegal Activity",
                value="illegal_activity",
                description="The message encourages illegal activity.",
                is_default=False,
                emoji=None,
            ),
            hikari.SelectMenuOption(
                label="Good Quality",
                value="good_quality",
                description="The message is good quality.",
                is_default=False,
                emoji=None,
            ),
            hikari.SelectMenuOption(
                label="Bad Quality",
                value="bad_quality",
                description="The message is bad quality.",
                is_default=False,
                emoji=None,
            ),
            hikari.SelectMenuOption(
                label="Spam",
                value="spam",
                description="The message is spam.",
                is_default=False,
                emoji=None,
            ),
        ],
        min_values=1,
        max_values=1,
    )
    async def label_select(self, select: miru.Select, ctx: miru.ViewContext) -> None:
        """Handle the select menu."""
        label = select.values[0]
        modal = LabelModal(label, self.content, title=f"Text Label: {label}", timeout=60)
        await modal.send(ctx.interaction)
        await modal.wait()

        self.stop()


@plugin.command
@lightbulb.command("Label Message", "Label a message")
@lightbulb.implements(lightbulb.MessageCommand)
async def label_message_text(ctx: lightbulb.MessageContext):
    """Label a message."""
    # We have to do some funny interaction chaining because discord only allows one component (select or modal) per interaction
    # so the select menu will open the modal

    msg: hikari.Message = ctx.options.target
    # Exit if the message is empty
    if not msg.content:
        await ctx.respond("Cannot label an empty message.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    # Send the select menu
    # The modal will be opened from the select menu interaction
    embed = hikari.Embed(title="Label Message", description="Select a label for the message.", color=DISCORD_GRAY)
    label_select_view = LabelSelect(
        msg.content,
        timeout=60,
    )
    resp = await ctx.respond(embed=embed, components=label_select_view, flags=hikari.MessageFlag.EPHEMERAL)

    await label_select_view.start(await resp.message())
    await label_select_view.wait()


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
