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
    assistant_reply_messages,
    confirm_label_response_message,
    confirm_ranking_response_message,
    confirm_text_response_message,
    initial_prompt_messages,
    label_assistant_reply_messages,
    label_prompter_reply_messages,
    plain_embed,
    prompter_reply_messages,
    rank_assistant_reply_message,
    rank_conversation_reply_messages,
    rank_initial_prompts_messages,
    rank_prompter_reply_messages,
    task_complete_embed,
)
from bot.settings import Settings
from loguru import logger
from oasst_shared.api_client import OasstApiClient
from oasst_shared.schemas import protocol as protocol_schema

plugin = lightbulb.Plugin("WorkPlugin")

MAX_TASK_TIME = 60 * 60  # seconds
MAX_TASK_ACCEPT_TIME = 60 * 10  # seconds

settings = Settings()

_Task_contra = t.TypeVar("_Task_contra", bound=protocol_schema.Task, contravariant=True)


class _TaskHandler(t.Generic[_Task_contra]):
    """Handle user interaction for a task."""

    def __init__(self, ctx: lightbulb.Context, task: _Task_contra) -> None:
        """Create a new `TaskHandler`.

        Args:
            ctx (lightbulb.Context): The context of the command that started the task.
            task (_Task_contra): The task to handle.
        """
        self.ctx = ctx
        self.task = task
        self.task_messages = self.get_task_messages(task)
        self.sent_messages: list[hikari.Message] = []

    @staticmethod
    def get_task_messages(task: _Task_contra) -> list[str]:
        """Get the messages to send to the user for the task."""
        raise NotImplementedError

    async def send(self) -> t.Literal["accept", "next", "cancel"] | None:
        """Send the task and wait for the user to accept/skip/cancel it."""
        # Send all but the last message because we need to attach buttons to the last one
        logger.debug(f"Sending {len(self.task_messages)} messages\n{self.task_messages!r}")
        for task_msg in self.task_messages[:-1]:
            if len(task_msg) > 2000:
                logger.warning(f"Attempting to send a message <2000 characters in length. Task id: {self.task.id}")
                task_msg = task_msg[:1999]
            self.sent_messages.append(await self.ctx.author.send(task_msg))

        # Send the last message with buttons
        task_accept_view = TaskAcceptView(timeout=MAX_TASK_ACCEPT_TIME)
        logger.debug(f"TH Message length {len(self.task_messages[-1])}")
        last_msg = await self.ctx.author.send(self.task_messages[-1][:1999], components=task_accept_view)

        await task_accept_view.start(last_msg)
        await task_accept_view.wait()

        return task_accept_view.choice

    async def handle(self) -> None:
        """Handle the user's response to the task.

        This method should be called after `send` has been called."""
        # Ack task to the backend
        oasst_api: OasstApiClient = self.ctx.bot.d.oasst_api
        await oasst_api.ack_task(self.task.id, message_id=f"{self.sent_messages[0].id}")

        # Loop until the user's input is accepted
        while True:
            try:
                # Wait for user to send a message
                event = await self.ctx.bot.wait_for(
                    hikari.DMMessageCreateEvent,
                    predicate=lambda e: (
                        e.author_id == self.ctx.author.id
                        and e.message.content is not None
                        and not e.message.content.startswith(settings.prefix)
                    ),
                    timeout=MAX_TASK_TIME,
                )

                # Validate the message
                if event.content is None or not self.check_user_input(event.content):
                    await self.ctx.author.send("Invalid input")
                    continue

                # Confirm user input
                if not (await self.confirm_user_input(event.content)):
                    continue

                # Message is valid and confirmed by user
                break

            except asyncio.TimeoutError:
                return

        next_task = await self.notify(event.content, event)
        if not isinstance(next_task, protocol_schema.TaskDone):
            raise TypeError(f"Unknown task type: {next_task!r}")

        return

    async def notify(self, content: str, event: hikari.DMMessageCreateEvent) -> protocol_schema.Task:
        """Notify the backend that the user completed the task."""
        raise NotImplementedError

    async def confirm_user_input(self, content: str) -> bool:
        """Send the user's response back to the user and ask them to confirm it. Returns True if the user confirms."""
        raise NotImplementedError

    def check_user_input(self, content: str) -> bool:
        """Check the user's response to the task. Returns True if the response is valid."""
        raise NotImplementedError

    async def cancel(self, reason: str = "not specified") -> None:
        """Cancel the task."""
        oasst_api: OasstApiClient = self.ctx.bot.d.oasst_api
        await oasst_api.nack_task(self.task.id, reason)


_Ranking_contra = t.TypeVar(
    "_Ranking_contra",
    bound=protocol_schema.RankAssistantRepliesTask
    | protocol_schema.RankInitialPromptsTask
    | protocol_schema.RankPrompterRepliesTask
    | protocol_schema.RankConversationRepliesTask,
    contravariant=True,
)


class _RankingTaskHandler(_TaskHandler[_Ranking_contra]):
    """This should not be used directly. Use its subclasses instead."""

    async def notify(self, content: str, event: hikari.DMMessageCreateEvent) -> protocol_schema.Task:
        oasst_api: OasstApiClient = self.ctx.bot.d.oasst_api

        task = await oasst_api.post_interaction(
            protocol_schema.MessageRanking(
                user=protocol_schema.User(
                    id=f"{self.ctx.author.id}", auth_method="discord", display_name=self.ctx.author.username
                ),
                ranking=[int(r) - 1 for r in content.split(",")],
                message_id=f"{self.sent_messages[0].id}",
            )
        )

        db: Connection = self.ctx.bot.d.db
        async with db.cursor() as cursor:
            row = await (
                await cursor.execute("SELECT log_channel_id FROM guilds WHERE guild_id = ?", (self.ctx.guild_id,))
            ).fetchone()
            log_channel = row[0] if row else None
        log_messages: list[hikari.Message] = []

        if log_channel is not None:
            for message in self.task_messages[:-1]:
                msg = await self.ctx.bot.rest.create_message(log_channel, message)
                log_messages.append(msg)
            await self.ctx.bot.rest.create_message(log_channel, task_complete_embed(self.task, self.ctx.author.mention))

        return task


class RankAssistantRepliesHandler(_RankingTaskHandler[protocol_schema.RankAssistantRepliesTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.RankAssistantRepliesTask) -> list[str]:
        return rank_assistant_reply_message(task)

    def check_user_input(self, content: str) -> bool:
        return len(content.split(",")) == len(self.task.reply_messages) and all(
            [r.isdigit() and int(r) in range(1, len(self.task.reply_messages) + 1) for r in content.split(",")]
        )

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(
            confirm_ranking_response_message(content, self.task.reply_messages), components=confirm_input_view
        )
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class RankInitialPromptHandler(_RankingTaskHandler[protocol_schema.RankInitialPromptsTask]):
    def __init__(self, ctx: lightbulb.Context, task: protocol_schema.RankInitialPromptsTask) -> None:
        super().__init__(ctx, task)

    @staticmethod
    def get_task_messages(task: protocol_schema.RankInitialPromptsTask) -> list[str]:
        return rank_initial_prompts_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content.split(",")) == len(self.task.prompt_messages) and all(
            [r.isdigit() and int(r) in range(1, len(self.task.prompt_messages) + 1) for r in content.split(",")]
        )

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(
            confirm_ranking_response_message(content, self.task.prompt_messages), components=confirm_input_view
        )
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class RankPrompterReplyHandler(_RankingTaskHandler[protocol_schema.RankPrompterRepliesTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.RankPrompterRepliesTask) -> list[str]:
        return rank_prompter_reply_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content.split(",")) == len(self.task.reply_messages) and all(
            [r.isdigit() and int(r) in range(1, len(self.task.reply_messages) + 1) for r in content.split(",")]
        )

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(
            confirm_ranking_response_message(content, self.task.reply_messages), components=confirm_input_view
        )
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class RankConversationReplyHandler(_RankingTaskHandler[protocol_schema.RankConversationRepliesTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.RankConversationRepliesTask) -> list[str]:
        return rank_conversation_reply_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content.split(",")) == len(self.task.reply_messages) and all(
            [r.isdigit() and int(r) in range(1, len(self.task.reply_messages) + 1) for r in content.split(",")]
        )

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(
            confirm_ranking_response_message(content, self.task.reply_messages), components=confirm_input_view
        )
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class InitialPromptHandler(_TaskHandler[protocol_schema.InitialPromptTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.InitialPromptTask) -> list[str]:
        return initial_prompt_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content) > 0

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(confirm_text_response_message(content), components=confirm_input_view)
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class PrompterReplyHandler(_TaskHandler[protocol_schema.PrompterReplyTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.PrompterReplyTask) -> list[str]:
        return prompter_reply_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content) > 0

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(confirm_text_response_message(content), components=confirm_input_view)
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class AssistantReplyHandler(_TaskHandler[protocol_schema.AssistantReplyTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.AssistantReplyTask) -> list[str]:
        return assistant_reply_messages(task)

    def check_user_input(self, content: str) -> bool:
        return len(content) > 0

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(confirm_text_response_message(content), components=confirm_input_view)
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


_Label_contra = t.TypeVar("_Label_contra", bound=protocol_schema.LabelConversationReplyTask, contravariant=True)


class _LabelConversationReplyHandler(_TaskHandler[_Label_contra]):
    def check_user_input(self, content: str) -> bool:
        user_labels = content.split(",")
        return (
            all([l in self.task.valid_labels for l in user_labels])
            and self.task.mandatory_labels is not None
            and all([m in user_labels for m in self.task.mandatory_labels])
        )

    async def confirm_user_input(self, content: str) -> bool:
        confirm_input_view = YesNoView()
        msg = await self.ctx.author.send(confirm_label_response_message(content), components=confirm_input_view)
        await confirm_input_view.start(msg)
        await confirm_input_view.wait()

        return bool(confirm_input_view.choice)


class LabelAssistantReplyHandler(_LabelConversationReplyHandler[protocol_schema.LabelAssistantReplyTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.LabelAssistantReplyTask) -> list[str]:
        return label_assistant_reply_messages(task)


class LabelPrompterReplyHandler(_LabelConversationReplyHandler[protocol_schema.LabelPrompterReplyTask]):
    @staticmethod
    def get_task_messages(task: protocol_schema.LabelPrompterReplyTask) -> list[str]:
        return label_prompter_reply_messages(task)


summarize_story = "summarize_story"
rate_summary = "rate_summary"


@plugin.command
@lightbulb.command("work", "Complete a task.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def work2(ctx: lightbulb.Context) -> None:
    """Complete a task."""
    oasst_api: OasstApiClient = ctx.bot.d.oasst_api
    currently_working: dict[hikari.Snowflake, UUID] = ctx.bot.d.currently_working

    # Check if the user is already working on a task
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
                task_id = currently_working[ctx.author.id]
                await oasst_api.nack_task(task_id, reason="user cancelled")

    if ctx.guild_id:
        await ctx.respond("check DMs", flags=hikari.MessageFlag.EPHEMERAL)

    # Keep sending tasks until the user doesn't want more
    try:
        while True:
            task = await oasst_api.fetch_random_task(
                user=protocol_schema.User(
                    id=f"{ctx.author.id}", display_name=ctx.author.username, auth_method="discord"
                ),
            )

            # Ranking tasks
            if isinstance(task, protocol_schema.RankAssistantRepliesTask):
                task_handler = RankAssistantRepliesHandler(ctx, task)
            elif isinstance(task, protocol_schema.RankInitialPromptsTask):
                task_handler = RankInitialPromptHandler(ctx, task)
            elif isinstance(task, protocol_schema.RankPrompterRepliesTask):
                task_handler = RankPrompterReplyHandler(ctx, task)
            elif isinstance(task, protocol_schema.RankConversationRepliesTask):
                task_handler = RankConversationReplyHandler(ctx, task)

            # Text input tasks
            elif isinstance(task, protocol_schema.InitialPromptTask):
                task_handler = InitialPromptHandler(ctx, task)
            elif isinstance(task, protocol_schema.PrompterReplyTask):
                task_handler = PrompterReplyHandler(ctx, task)
            elif isinstance(task, protocol_schema.AssistantReplyTask):
                task_handler = AssistantReplyHandler(ctx, task)

            # Label tasks
            elif isinstance(task, protocol_schema.LabelAssistantReplyTask):
                task_handler = LabelAssistantReplyHandler(ctx, task)
            elif isinstance(task, protocol_schema.LabelPrompterReplyTask):
                task_handler = LabelPrompterReplyHandler(ctx, task)

            else:
                raise ValueError(f"Unknown task type: {type(task)}")

            resp = await task_handler.send()

            match resp:
                case "accept":
                    currently_working[ctx.author.id] = task.id
                    await task_handler.handle()
                case "next":
                    await task_handler.cancel("user skipped task")
                case "cancel":
                    await task_handler.cancel("user canceled work")
                    break
                case None:
                    await task_handler.cancel("select timed out")
                    break
    finally:
        del currently_working[ctx.author.id]


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
