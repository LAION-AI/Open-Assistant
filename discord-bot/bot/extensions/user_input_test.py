"""Task plugin for testing different data collection methods."""
# TODO: Delete this once user input method has been decided for final bot.
import asyncio
import typing as t
from datetime import datetime, timedelta

import hikari
import lightbulb
import lightbulb.decorators
import miru
from bot.utils import format_time
from oasst_shared.schemas.protocol import TaskRequestType

plugin = lightbulb.Plugin("TaskPlugin")

MAX_TASK_TIME = 60 * 60
MAX_TASK_ACCEPT_TIME = 60


@plugin.command
@lightbulb.option(
    "type",
    "The type of task to request.",
    choices=[hikari.CommandChoice(name=task.split(".")[-1], value=task) for task in TaskRequestType],
    required=False,
    default=TaskRequestType.summarize_story,
    type=str,
)
@lightbulb.command("task_thread", "Request a task from the backend.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def task_thread(ctx: lightbulb.SlashContext):
    """Request a task from the backend."""
    typ: str = ctx.options.type

    # Create a thread for the task
    thread = await ctx.bot.rest.create_thread(ctx.channel_id, hikari.ChannelType.GUILD_PUBLIC_THREAD, f"Task: {typ}")

    await ctx.respond(f"Please complete the task in the thread: {thread.mention}")

    # Send the task in the thread
    await thread.send(
        f"""\
Please complete the task.
Sample Task

Self destruct {format_time(datetime.now() + timedelta(seconds=MAX_TASK_TIME), 'R')}
"""
    )

    # Wait for the user to respond
    try:
        event = await ctx.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=MAX_TASK_TIME,
            predicate=lambda e: e.author.id == ctx.author.id and e.channel_id == thread.id,
        )
        await ctx.respond(f"Received message: {event.message.content}")
    except asyncio.TimeoutError:
        await ctx.respond("You took too long to respond.")
    finally:
        await thread.delete()


@plugin.command
@lightbulb.option(
    "type",
    "The type of task to request.",
    choices=[hikari.CommandChoice(name=task.split(".")[-1], value=task) for task in TaskRequestType],
    required=False,
    default=TaskRequestType.summarize_story,
    type=str,
)
@lightbulb.command("task_dm", "Request a task from the backend.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def task_dm(ctx: lightbulb.Context):
    """Request a task from the backend."""
    await ctx.respond("Please complete the task in your DMs")

    # Send the task in the dm
    await ctx.author.send(
        f"""\
Please complete the task.
Sample Task

Self destruct {format_time(datetime.now() + timedelta(seconds=MAX_TASK_TIME), 'R')}
"""
    )

    # Wait for the user to respond
    try:
        event = await ctx.bot.wait_for(
            hikari.DMMessageCreateEvent,
            timeout=MAX_TASK_TIME,
            predicate=lambda e: e.author.id == ctx.author.id,
        )
        await ctx.respond(f"Received message: {event.message.content}")
    except asyncio.TimeoutError:
        await ctx.respond("You took too long to respond.")


class TaskModal(miru.Modal):
    """Modal for submitting a task."""

    response = miru.TextInput(
        label="Response",
        placeholder="Enter your response!",
        required=True,
        style=hikari.TextInputStyle.PARAGRAPH,
        row=2,
    )

    async def callback(self, context: miru.ModalContext) -> None:
        await context.respond(f"Received response: {self.response.value}", flags=hikari.MessageFlag.EPHEMERAL)


class ModalView(miru.View):
    """View for opening a modal."""

    def __init__(self, modal_title: str, task: str, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.modal_title = modal_title
        self.task = task

    @miru.button(label="Start Task!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = TaskModal(title=self.modal_title)
        modal.add_item(miru.TextInput(label="Task", value=self.task, style=hikari.TextInputStyle.PARAGRAPH, row=1))
        await ctx.respond_with_modal(modal)


@plugin.command
@lightbulb.option(
    "type",
    "The type of task to request.",
    choices=[hikari.CommandChoice(name=task.split(".")[-1], value=task) for task in TaskRequestType],
    required=False,
    default=TaskRequestType.summarize_story,
    type=str,
)
@lightbulb.command("task_modal", "Request a task from the backend.", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def task_modal(ctx: lightbulb.SlashContext):
    """Request a task from the backend."""
    # typ: str = ctx.options.type
    view = ModalView(
        modal_title="Assistant Response",
        task="Please explain the moon landing to a six year old.",
        timeout=MAX_TASK_TIME,
    )
    resp = await ctx.respond(
        "Task - Respond to the prompt as if you were the Assistant:",
        flags=hikari.MessageFlag.EPHEMERAL,
        components=view,
    )
    await view.start(await resp.message())


class RatingView(miru.View):
    """View for rating a task."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.presses: list[str] = []

    def _close_if_all_pressed(self) -> None:
        if len(self.presses) == 5:
            self.stop()

    @miru.button(label="1", style=hikari.ButtonStyle.PRIMARY)
    async def button_1(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if button.label not in self.presses:
            self.presses.append("1")
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)
        self._close_if_all_pressed()

    @miru.button(label="2", style=hikari.ButtonStyle.PRIMARY)
    async def button_2(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if button.label not in self.presses:
            self.presses.append("2")
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)
        self._close_if_all_pressed()

    @miru.button(label="3", style=hikari.ButtonStyle.PRIMARY)
    async def button_3(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if button.label not in self.presses:
            self.presses.append("3")
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)
        self._close_if_all_pressed()

    @miru.button(label="4", style=hikari.ButtonStyle.PRIMARY)
    async def button_4(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if button.label not in self.presses:
            self.presses.append("4")
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)
        self._close_if_all_pressed()

    @miru.button(label="5", style=hikari.ButtonStyle.PRIMARY)
    async def button_5(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if button.label not in self.presses:
            self.presses.append("5")
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)
        self._close_if_all_pressed()

    @miru.button(label="Reset", style=hikari.ButtonStyle.DANGER)
    async def reset_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.presses = []
        await ctx.respond(f"Received response: {button.label}", flags=hikari.MessageFlag.EPHEMERAL)


class SelectRating(miru.View):
    """View for rating a task with a select menu."""

    @miru.select(
        options=[
            hikari.SelectMenuOption(
                label="1",
                value="1",
                description=None,
                emoji=None,
                is_default=False,
            ),
            hikari.SelectMenuOption(
                label="2",
                value="2",
                description=None,
                emoji=None,
                is_default=False,
            ),
            hikari.SelectMenuOption(
                label="3",
                value="3",
                description=None,
                emoji=None,
                is_default=False,
            ),
        ],
        placeholder="Select the good responses",
        min_values=0,
        max_values=3,
        row=3,
    )
    async def select(self, select: miru.Select, ctx: miru.ViewContext) -> None:
        await ctx.respond(f"You selected {select.values}", flags=hikari.MessageFlag.EPHEMERAL)


@plugin.command
@lightbulb.command("rating_task", "Rate stuff.")
@lightbulb.implements(lightbulb.SlashCommand)
async def rating_task(ctx: lightbulb.SlashContext):
    """Rate stuff."""
    # Message Based rating
    await ctx.respond(
        "List the responses in order of best to worst response (1,2,3,4,5)", flags=hikari.MessageFlag.EPHEMERAL
    )
    try:
        event = await ctx.bot.wait_for(
            hikari.MessageCreateEvent, timeout=MAX_TASK_TIME, predicate=lambda e: e.author.id == ctx.author.id
        )

    except asyncio.TimeoutError:
        await ctx.respond("Timed out waiting for response")
        return

    if event.content is None:
        await ctx.respond("No content in message")
        return
    ratings = event.content.replace(" ", "").split(",")

    # Check if the ratings are valid
    if len(ratings) != 5:
        await ctx.respond("Invalid number of ratings")
    if not all([rating in ("1", "2", "3", "4", "5") for rating in ratings]):
        await ctx.respond("Invalid rating")

    await ctx.respond(f"Your responses: {ratings}", flags=hikari.MessageFlag.EPHEMERAL)
    # Button Based rating
    view = RatingView(timeout=MAX_TASK_TIME)

    resp = await ctx.respond("Click the buttons in order of best to worst response", components=view)
    await view.start(await resp.message())
    await view.wait()
    await ctx.respond(f"Your responses: {view.presses}", flags=hikari.MessageFlag.EPHEMERAL)
    await resp.delete()

    # Select Based rating
    select_view = SelectRating(timeout=MAX_TASK_TIME)
    resp_2 = await ctx.respond("Select the good responses", components=select_view, flags=hikari.MessageFlag.EPHEMERAL)
    await select_view.start(await resp_2.message())
    await select_view.wait()
    await resp_2.delete()


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
