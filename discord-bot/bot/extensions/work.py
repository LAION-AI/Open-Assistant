# -*- coding: utf-8 -*-
"""Work plugin for collecting user data."""
import asyncio
import logging
import typing as t
from datetime import datetime

import hikari
import lightbulb
import lightbulb.decorators
import miru
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.schemas.protocol import TaskRequestType

from bot.api_client import OasstApiClient, TaskType
from bot.utils import ZWJ

plugin = lightbulb.Plugin("WorkPlugin")

MAX_TASK_TIME = 60 * 60  # 1 hour
MAX_TASK_ACCEPT_TIME = 60  # 1 minute

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@plugin.command
@lightbulb.option(
    "type",
    "The type of task to request.",
    choices=[hikari.CommandChoice(name=task.value, value=task) for task in TaskRequestType],
    required=False,
    default=str(TaskRequestType.rank_initial_prompts),  # TODO: change back to random
    type=str,
)
@lightbulb.command("work", "Complete a task.")
@lightbulb.implements(lightbulb.SlashCommand)
async def work(ctx: lightbulb.SlashContext):
    """Create and handle a task."""
    task_type: TaskRequestType = TaskRequestType(ctx.options.type)

    await ctx.respond("Sending you a task, check your DMs", flags=hikari.MessageFlag.EPHEMERAL)
    logger.debug(f"task_type: {task_type!r}, task_type type {type(task_type)}")

    await _handle_task(ctx, task_type)


async def _handle_task(ctx: lightbulb.SlashContext, task_type: TaskRequestType) -> None:
    """Handle creating and collecting user input for a task.

    Continually present tasks to the user until they select one, cancel, or time out.
    If they select one, present the task steps until a `task_done` task is received.
    Finally, ask the user if they want to perform another task (of the same type).
    """
    oasst_api: OasstApiClient = ctx.bot.d.oasst_api

    # Continue to complete tasks until the user doesn't want to do another
    done = False
    while not done:

        # Loop until the user accepts a task
        task, msg_id = await _select_task(ctx, task_type)

        if task is None:
            return

        # Task action loop
        completed = False
        while not completed:
            await ctx.author.send("Please type your response here:")
            try:
                event = await ctx.bot.wait_for(
                    hikari.DMMessageCreateEvent, timeout=MAX_TASK_TIME, predicate=lambda e: e.author.id == ctx.author.id
                )
            except asyncio.TimeoutError:
                await ctx.author.send("Task timed out. Exiting")
                # TODO: NACK task maybe?
                return

            # Invalid response
            if event.content is None:
                await ctx.author.send("No content in message")
                continue

            logger.info(f"User input received: {event.content}")

            # Send the response to the backend
            reply = protocol_schema.TextReplyToPost(
                post_id=str(msg_id),
                user_post_id=str(event.message_id),
                user=protocol_schema.User(
                    auth_method="discord", id=str(ctx.author.id), display_name=ctx.author.username
                ),
                text=event.content,
            )
            logger.debug(f"Sending reply to backend: {reply!r}")

            # Get next task
            new_task = await oasst_api.post_interaction(reply)
            logger.info(f"New task {new_task}")

            if new_task.type == TaskType.done:
                await ctx.author.send("Task completed")
                completed = True
                continue
            else:
                logger.fatal(f"Unexpected task type received: {new_task.type}")

        # ask the user if they want to do another task
        choice_view = ChoiceView(timeout=MAX_TASK_ACCEPT_TIME)
        msg = await ctx.author.send("Would you like another task?", components=choice_view)
        await choice_view.start(msg)
        await choice_view.wait()

        match choice_view.choice:
            case False | None:
                done = True
                await ctx.author.send("Exiting, goodbye!")
            case True:
                pass


async def _select_task(
    ctx: lightbulb.SlashContext, task_type: TaskRequestType, user: protocol_schema.User | None = None
) -> tuple[protocol_schema.Task | None, str]:
    """Present tasks to the user until they accept one, cancel, or time out."""
    oasst_api: OasstApiClient = ctx.bot.d.oasst_api
    logger.debug(f"Starting task selection for {task_type}")

    # Loop until the user accepts a task, cancels, or times out
    while True:
        logger.debug(f"Requesting task of type {task_type}")
        task = await oasst_api.fetch_task(task_type, user)
        resp, msg_id = await _send_task(ctx, task)

        logger.debug(f"user choice: {resp}")
        match resp:
            case "accept":
                logger.info(f"Task {task.id} accepted, sending ACK")
                await oasst_api.ack_task(task.id, msg_id)
                return task, msg_id

            case "next":
                logger.info(f"Task {task.id} rejected, sending NACK")
                await oasst_api.nack_task(task.id, "rejected")
                await ctx.author.send("Sending next task...")
                continue

            case "cancel":
                logger.info(f"Task {task.id} canceled, sending NACK")
                await oasst_api.nack_task(task.id, "canceled")
                await ctx.author.send("Task canceled. Exiting")
                return None, msg_id

            case None:
                logger.info(f"Task {task.id} timed out, sending NACK")
                await oasst_api.nack_task(task.id, "timed out")
                await ctx.author.send("Task timed out. Exiting")
                return None, msg_id


async def _send_task(
    ctx: lightbulb.SlashContext, task: protocol_schema.Task
) -> tuple[t.Literal["accept", "next", "cancel"] | None, str]:
    """Send a task to the user.

    Returns the user's choice and the message ID of the task message.
    """
    # The clean way to do this would be to attach a `to_embed` method to the task classes
    # but the tasks aren't discord specific so that doesn't really make sense.

    view = TaskAcceptView(timeout=MAX_TASK_ACCEPT_TIME)
    embed: hikari.UndefinedOr[hikari.Embed] = hikari.UNDEFINED

    # Create an embed based on the task's type
    if task.type == TaskRequestType.initial_prompt:
        assert isinstance(task, protocol_schema.InitialPromptTask)
        logger.info("sending initial prompt task")
        embed = _initial_prompt_embed(task)

    elif task.type == TaskRequestType.rank_initial_prompts:
        assert isinstance(task, protocol_schema.RankInitialPromptsTask)
        logger.info("sending rank initial prompt task")
        embed = _rank_initial_prompt_embed(task)

    else:
        logger.error(f"unknown task type {task.type}")

    msg = await ctx.author.send(
        ZWJ,
        embed=embed,
        components=view,
    )

    assert msg is not None

    await view.start(msg)
    await view.wait()

    return view.choice, str(msg.id)


def _initial_prompt_embed(task: protocol_schema.InitialPromptTask) -> hikari.Embed:
    return (
        hikari.Embed(title="Initial Prompt", description=f"Hint: {task.hint}", timestamp=datetime.now().astimezone())
        .set_image("https://images.unsplash.com/photo-1455390582262-044cdead277a?w=512")
        .set_footer(text=f"OASST Assistant | {task.id}")
    )


def _rank_initial_prompt_embed(task: protocol_schema.RankInitialPromptsTask) -> hikari.Embed:
    embed = (
        hikari.Embed(
            title="Rank Initial Prompt",
            description="Rank the following tasks from best to worst (1,2,3,4,5)",
            timestamp=datetime.now().astimezone(),
        )
        .set_image("https://images.unsplash.com/photo-1455390582262-044cdead277a?w=512")
        .set_footer(text=f"OASST Assistant | {task.id}")
    )

    for i, prompt in enumerate(task.prompts):
        embed.add_field(name=f"Prompt {i + 1}", value=prompt, inline=False)

    return embed


class TaskAcceptView(miru.View):
    """View with three buttons: accept, next, and cancel.

    The view stops once one of the buttons is pressed and the choice is stored in the `choice` attribute.
    """

    choice: t.Literal["accept", "next", "cancel"] | None = None

    @miru.button(label="Accept", custom_id="accept", row=0, style=hikari.ButtonStyle.SUCCESS)
    async def accept_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Accept button pressed")
        self.choice = "accept"
        self.stop()

    @miru.button(label="Next Task", custom_id="next_task", row=0, style=hikari.ButtonStyle.SECONDARY)
    async def next_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Next button pressed")
        self.choice = "next"
        self.stop()

    @miru.button(label="Cancel", custom_id="cancel", row=0, style=hikari.ButtonStyle.DANGER)
    async def cancel_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Cancel button pressed")
        self.choice = "cancel"
        self.stop()


class ChoiceView(miru.View):
    """View with two buttons: yes and no.

    The view stops once one of the buttons is pressed and the choice is stored in the `choice` attribute.
    """

    choice: bool | None = None

    @miru.button(label="Yes", custom_id="yes", style=hikari.ButtonStyle.SUCCESS)
    async def yes_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.choice = True
        self.stop()

    @miru.button(label="No", custom_id="no", style=hikari.ButtonStyle.DANGER)
    async def no_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.choice = False
        self.stop()


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
