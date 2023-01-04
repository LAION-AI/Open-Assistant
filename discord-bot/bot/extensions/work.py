"""Work plugin for collecting user data."""
import asyncio
import typing as t
from uuid import UUID

import hikari
import lightbulb
import lightbulb.decorators
import miru
from aiosqlite import Connection
from bot.messages import (
    assistant_reply_message,
    confirm_ranking_response_message,
    confirm_text_response_message,
    initial_prompt_message,
    invalid_user_input_embed,
    plain_embed,
    prompter_reply_message,
    rank_assistant_reply_message,
    rank_initial_prompts_message,
    rank_prompter_reply_message,
    task_complete_embed,
)
from bot.settings import Settings
from loguru import logger
from oasst_shared.api_client import OasstApiClient, TaskType
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.schemas.protocol import TaskRequestType

plugin = lightbulb.Plugin("WorkPlugin")

MAX_TASK_TIME = 60 * 60  # seconds
MAX_TASK_ACCEPT_TIME = 60 * 10  # seconds

settings = Settings()


@plugin.command
@lightbulb.option(
    "type",
    "The type of task to request.",
    choices=[hikari.CommandChoice(name=task.value, value=task) for task in TaskRequestType],
    required=False,
    default=str(TaskRequestType.random),
    type=str,
)
@lightbulb.command("work", "Complete a task.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def work(ctx: lightbulb.Context):
    """Create and handle a task."""
    # Only send this message if started from a server
    if ctx.guild_id is not None:
        await ctx.respond(embed=plain_embed("Sending you a task, check your DMs"), flags=hikari.MessageFlag.EPHEMERAL)

    # make sure the user isn't currently doing a task, and if they are, ask if they want to cancel it
    currently_working: dict[
        hikari.Snowflakeish, tuple[hikari.Message | None, UUID | None]
    ] = ctx.bot.d.currently_working

    oasst_api: OasstApiClient = ctx.bot.d.oasst_api
    if ctx.author.id in currently_working:
        yn_view = YesNoView(timeout=MAX_TASK_ACCEPT_TIME)
        msg = await ctx.author.send(
            embed=plain_embed("You are already working. Would you like to cancel your old task start a new one?"),
            flags=hikari.MessageFlag.EPHEMERAL,
            components=yn_view,
        )
        await yn_view.start(msg)
        await yn_view.wait()

        match yn_view.choice:
            case False | None:
                return
            case True:
                old_msg, task_id = currently_working[ctx.author.id]
                if old_msg is not None:
                    logger.info(f"User {ctx.author.id} cancelled task {task_id}, deleting message {old_msg.id}")
                    map(lambda c: c, old_msg.components)
                    await old_msg.delete()
                if task_id is not None:
                    await oasst_api.nack_task(task_id, reason="user cancelled")

        await msg.delete()

    currently_working[ctx.author.id] = (None, None)

    # Create a TaskRequestType from the stringified enum value
    task_type: TaskRequestType = TaskRequestType(ctx.options.type.split(".")[-1])

    logger.debug(f"Starting task_type: {task_type!r}")
    try:
        await _handle_task(ctx, task_type)
    finally:
        del currently_working[ctx.author.id]


async def _handle_task(ctx: lightbulb.Context, task_type: TaskRequestType) -> None:
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
            # User cancelled
            return

        # Task action loop
        completed = False
        while not completed:
            await ctx.author.send(embed=plain_embed("Please type your response below:"))
            try:
                event = await ctx.bot.wait_for(
                    hikari.DMMessageCreateEvent,
                    timeout=MAX_TASK_TIME,
                    predicate=lambda e: e.author.id == ctx.author.id
                    and not (e.message.content or "").startswith(settings.prefix),
                )
            except asyncio.TimeoutError:
                await ctx.author.send(embed=plain_embed("Task timed out. Exiting"))
                await oasst_api.nack_task(task.id, reason="timed out")
                logger.info(f"Task {task.id} timed out")
                return

            # Invalid response
            valid, err_msg = _validate_user_input(event.content, task)
            if not valid or event.content is None:

                await ctx.author.send(embed=invalid_user_input_embed(err_msg))
                continue

            logger.debug(f"Successful user input received: {event.content}")

            # Confirm user input
            if isinstance(task, protocol_schema.RankConversationRepliesTask):
                content = confirm_ranking_response_message(event.content, task.replies)
            elif isinstance(task, protocol_schema.RankInitialPromptsTask):
                content = confirm_ranking_response_message(event.content, task.prompts)
            elif isinstance(task, protocol_schema.ReplyToConversationTask | protocol_schema.InitialPromptTask):
                content = confirm_text_response_message(event.content)
            else:
                logger.critical(f"Unknown task type: {task.type}")
                raise ValueError(f"Unknown task type: {task.type}")

            confirm_resp_view = YesNoView(timeout=MAX_TASK_TIME)
            msg = await ctx.author.send(content, components=confirm_resp_view)
            await confirm_resp_view.start(msg)
            await confirm_resp_view.wait()

            match confirm_resp_view.choice:
                case False | None:
                    continue
                case True:
                    await msg.delete()  # buttons are already gone

            # Send the response to the backend
            if isinstance(task, protocol_schema.RankConversationRepliesTask | protocol_schema.RankInitialPromptsTask):
                reply = protocol_schema.MessageRanking(
                    message_id=str(msg_id),
                    ranking=[int(r) - 1 for r in event.content.replace(" ", "").split(",")],
                    user=protocol_schema.User(
                        auth_method="discord", id=str(ctx.author.id), display_name=ctx.author.username
                    ),
                )
            elif isinstance(task, protocol_schema.ReplyToConversationTask | protocol_schema.InitialPromptTask):
                reply = protocol_schema.TextReplyToMessage(
                    message_id=str(msg_id),
                    user_message_id=str(event.message_id),
                    user=protocol_schema.User(
                        auth_method="discord", id=str(ctx.author.id), display_name=ctx.author.username
                    ),
                    text=event.content,
                )
            else:
                logger.critical(f"Unexpected task type received: {task.type}")
                raise ValueError(f"Unexpected task type received: {task.type}")

            logger.debug(f"Sending reply to backend: {reply!r}")

            # Get next task
            new_task = await oasst_api.post_interaction(reply)
            logger.info(f"New task {new_task}")

            if new_task.type == TaskType.done:
                await ctx.author.send(embed=plain_embed("Task completed"))
                completed = True
                continue
            else:
                logger.critical(f"Unexpected task type received: {new_task.type}")

        # Send a message in all the log channels that the task is complete
        conn: Connection = ctx.bot.d.db
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT log_channel_id FROM guild_settings")
            log_channel_ids = await cursor.fetchall()

            channels = [
                ctx.bot.cache.get_guild_channel(id[0]) or await ctx.bot.rest.fetch_channel(id[0])
                for id in log_channel_ids
            ]

            done_embed = task_complete_embed(task, ctx.author.mention)
            # This will definitely get the bot rate limited, but that's a future problem
            asyncio.gather(*(ch.send(embed=done_embed) for ch in channels if isinstance(ch, hikari.TextableChannel)))

        # ask the user if they want to do another task
        another_task_view = YesNoView(timeout=MAX_TASK_ACCEPT_TIME)
        msg = await ctx.author.send(embed=plain_embed("Would you like another task?"), components=another_task_view)
        await another_task_view.start(msg)
        await another_task_view.wait()

        match another_task_view.choice:
            case False | None:
                done = True
                await msg.edit(embed=plain_embed("Exiting, goodbye!"))
            case True:
                pass


async def _select_task(
    ctx: lightbulb.Context, task_type: TaskRequestType, user: protocol_schema.User | None = None
) -> tuple[protocol_schema.Task | None, str]:
    """Present tasks to the user until they accept one, cancel, or time out."""
    oasst_api: OasstApiClient = ctx.bot.d.oasst_api
    logger.debug(f"Starting task selection for {task_type}")

    # Loop until the user accepts a task, cancels, or times out
    msg: hikari.UndefinedOr[hikari.Message] = hikari.UNDEFINED
    while True:
        logger.debug(f"Requesting task of type {task_type}")
        task = await oasst_api.fetch_task(task_type, user)
        resp, msg = await _send_task(ctx, task, msg)
        msg_id = str(msg.id)

        logger.debug(f"User choice: {resp}")
        match resp:
            case "accept":
                logger.info(f"Task {task.id} accepted, sending ACK")
                await oasst_api.ack_task(task.id, msg_id)
                return task, msg_id

            case "next":
                logger.info(f"Task {task.id} rejected, sending NACK")
                await oasst_api.nack_task(task.id, "rejected")
                continue

            case "cancel":
                logger.info(f"Task {task.id} canceled, sending NACK")
                await oasst_api.nack_task(task.id, "canceled")
                await ctx.author.send(embed=plain_embed("Task canceled. Exiting"))
                return None, msg_id

            case None:
                logger.info(f"Task {task.id} timed out, sending NACK")
                await oasst_api.nack_task(task.id, "timed out")
                await ctx.author.send(embed=plain_embed("Task timed out. Exiting"))
                return None, msg_id


async def _send_task(
    ctx: lightbulb.Context, task: protocol_schema.Task, msg: hikari.UndefinedOr[hikari.Message]
) -> tuple[t.Literal["accept", "next", "cancel"] | None, hikari.Message]:
    """Send a task to the user.

    Returns the user's choice and the message ID of the task message.
    """
    # The clean way to do this would be to attach a `to_embed` method to the task classes
    # but the tasks aren't discord specific so that doesn't really make sense.

    embed: hikari.UndefinedOr[hikari.Embed] = hikari.UNDEFINED
    content: hikari.UndefinedOr[str] = hikari.UNDEFINED

    # Create an embed based on the task's type
    if task.type == TaskRequestType.initial_prompt:
        assert isinstance(task, protocol_schema.InitialPromptTask)
        logger.debug("sending initial prompt task")
        content = initial_prompt_message(task)

    elif task.type == TaskRequestType.rank_initial_prompts:
        assert isinstance(task, protocol_schema.RankInitialPromptsTask)
        logger.debug("sending rank initial prompt task")
        content = rank_initial_prompts_message(task)

    elif task.type == TaskRequestType.rank_prompter_replies:
        assert isinstance(task, protocol_schema.RankPrompterRepliesTask)
        logger.debug("sending rank user reply task")
        content = rank_prompter_reply_message(task)

    elif task.type == TaskRequestType.rank_assistant_replies:
        assert isinstance(task, protocol_schema.RankAssistantRepliesTask)
        logger.debug("sending rank assistant reply task")
        content = rank_assistant_reply_message(task)

    elif task.type == TaskRequestType.prompter_reply:
        assert isinstance(task, protocol_schema.PrompterReplyTask)
        logger.debug("sending user reply task")
        content = prompter_reply_message(task)

    elif task.type == TaskRequestType.assistant_reply:
        assert isinstance(task, protocol_schema.AssistantReplyTask)
        logger.debug("sending assistant reply task")
        content = assistant_reply_message(task)

    elif task.type == TaskRequestType.summarize_story:
        raise NotImplementedError
    elif task.type == TaskRequestType.rate_summary:
        raise NotImplementedError

    else:
        logger.critical(f"unknown task type {task.type}")
        raise ValueError(f"unknown task type {task.type}")

    view = TaskAcceptView(timeout=MAX_TASK_ACCEPT_TIME)
    if not msg:
        msg = await ctx.author.send(
            content,
            embed=embed,
            components=view,
        )
    else:
        await msg.edit(
            content,
            embed=embed,
            components=view,
        )

    assert msg is not None

    # Set the choice id as the current msg id
    ctx.bot.d.currently_working[ctx.author.id] = (msg, task.id)

    await view.start(msg)
    await view.wait()

    return view.choice, msg


def _validate_user_input(content: str | None, task: protocol_schema.Task) -> tuple[bool, str]:
    """Returns whether the user's input is valid for the task type and an error message."""
    if content is None:
        return False, "No input provided"

    # User message input
    if (
        task.type == TaskRequestType.initial_prompt
        or task.type == TaskRequestType.prompter_reply
        or task.type == TaskRequestType.assistant_reply
    ):
        assert isinstance(
            task,
            protocol_schema.InitialPromptTask | protocol_schema.PrompterReplyTask | protocol_schema.AssistantReplyTask,
        )
        return len(content) > 0, "Message must be at least one character long."

    # Ranking tasks
    elif task.type == TaskRequestType.rank_prompter_replies or task.type == TaskRequestType.rank_assistant_replies:
        assert isinstance(task, protocol_schema.RankPrompterRepliesTask | protocol_schema.RankAssistantRepliesTask)
        num_replies = len(task.replies)

        rankings = content.replace(" ", "").split(",")
        return (
            set(rankings) == {str(i) for i in range(1, num_replies + 1)} and len(rankings) == num_replies,
            "Message must contain numbers for all replies.",
        )

    elif task.type == TaskRequestType.rank_initial_prompts:
        assert isinstance(task, protocol_schema.RankInitialPromptsTask)
        num_prompts = len(task.prompts)

        rankings = content.replace(" ", "").split(",")
        return (
            set(rankings) == {str(i) for i in range(1, num_prompts + 1)} and len(rankings) == num_prompts,
            "Message must contain numbers for all prompts.",
        )

    elif task.type == TaskRequestType.summarize_story:
        raise NotImplementedError
    elif task.type == TaskRequestType.rate_summary:
        raise NotImplementedError

    else:
        logger.critical(f"Unknown task type {task.type}")
        raise ValueError(f"Unknown task type {task.type}")


class TaskAcceptView(miru.View):
    """View with three buttons: accept, next, and cancel.

    The view stops once one of the buttons is pressed and the choice is stored in the `choice` attribute.
    """

    choice: t.Literal["accept", "next", "cancel"] | None = None

    @miru.button(label="Accept", custom_id="accept", row=0, style=hikari.ButtonStyle.SUCCESS)
    async def accept_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Accept button pressed")
        self.choice = "accept"
        await ctx.message.edit(component=None)
        self.stop()

    @miru.button(label="Next Task", custom_id="next_task", row=0, style=hikari.ButtonStyle.SECONDARY)
    async def next_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Next button pressed")
        self.choice = "next"
        await ctx.message.edit(component=None)
        self.stop()

    @miru.button(label="Cancel", custom_id="cancel", row=0, style=hikari.ButtonStyle.DANGER)
    async def cancel_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        logger.info("Cancel button pressed")
        self.choice = "cancel"
        await ctx.message.edit(component=None)
        self.stop()

    async def on_timeout(self) -> None:
        if self.message is not None:
            await self.message.edit(component=None)


class YesNoView(miru.View):
    """View with two buttons: yes and no.

    The view stops once one of the buttons is pressed and the choice is stored in the `choice` attribute.
    """

    choice: bool | None = None

    @miru.button(label="Yes", custom_id="yes", style=hikari.ButtonStyle.SUCCESS)
    async def yes_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.choice = True
        await ctx.message.edit(component=None)
        self.stop()

    @miru.button(label="No", custom_id="no", style=hikari.ButtonStyle.DANGER)
    async def no_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.choice = False
        await ctx.message.edit(component=None)
        self.stop()

    async def on_timeout(self) -> None:
        if self.message is not None:
            await self.message.edit(component=None)


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
