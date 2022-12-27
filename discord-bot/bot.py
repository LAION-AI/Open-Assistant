# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

import discord
import task_handlers
from api_client import ApiClient, TaskType
from bot_base import BotBase
from discord import app_commands
from discord.ext.commands import Bot
from loguru import logger
from events import OnReady, OnMessage
from message_templates import MessageTemplates
from oasst_shared.schemas import protocol as protocol_schema
from utils import get_git_head_hash, utcnow

__version__ = "0.0.3"
BOT_NAME = "Open-Assistant Junior"


class OpenAssistantBot(BotBase):
    def __init__(
        self,
        bot_token: str,
        bot_channel_name: str,
        backend_url: str,
        api_key: str,
        owner_id: Optional[Union[int, str]] = None,
        template_dir: str = "./templates",
        debug: bool = False,
    ):
        super().__init__()

        self.template_dir = Path(template_dir)
        self.bot_channel_name = bot_channel_name
        self.templates = MessageTemplates(template_dir)
        self.debug = debug

        intents = discord.Intents.default()
        intents.message_content = True

        if isinstance(owner_id, str):
            owner_id = int(owner_id)
        self.owner_id = owner_id

        self.bot_token = bot_token
        # Bot class inherits from discord.Client
        # this improves code structure for bigger projects
        bot = Bot(intents=intents)
        client = bot # to be compatible with the old code
        self.client = client
        self.loop = client.loop

        self.bot_channel: discord.TextChannel = None
        self.backend = ApiClient(backend_url, api_key)

        self.tree = app_commands.CommandTree(self.client, fallback_to_global=True)

        # register events
        bot.add_cog(OnReady(self, logger, bot_channel_name))
        bot.add_cog(OnMessage(self, logger))

        @self.tree.command()
        async def tutorial(interaction: discord.Interaction):
            """Start the Open-Assistant tutorial via DMs."""

            dm = await self.client.create_dm(discord.Object(interaction.user.id))
            await dm.send("Tutorial coming soon... :-)")
            await interaction.response.send_message(f"tutorial command by {interaction.user.name}")

        @self.tree.command()
        async def help(interaction: discord.Interaction):
            """Sends the user a list of all available commands"""
            await self.post_help(interaction.user)
            await interaction.response.send_message(f"@{interaction.user.display_name}, I've sent you a PM.")

        @self.tree.command()
        async def work(interaction: discord.Interaction):
            """Request a new personalized task"""

            # task = self.backend.fetch_task(protocol_schema.TaskRequestType.rate_summary, user=None)
            # task = self.backend.fetch_random_task(user=None)
            q = task_handlers.Questionnaire()
            await interaction.response.send_modal(q)

    async def post_help(self, user: discord.abc.User) -> discord.Message:
        is_bot_owner = user.id == self.owner_id
        return await self.post_template("help.msg", channel=user, is_bot_owner=is_bot_owner)

    async def post_boot_message(self) -> discord.Message:
        return await self.post_template(
            "boot.msg", bot_name=BOT_NAME, version=__version__, git_hash=get_git_head_hash(), debug=self.debug
        )

    async def post_welcome_message(self) -> discord.Message:
        return await self.post_template("welcome.msg")

    async def delete_all_old_bot_messages(self) -> None:
        logger.info("Deleting old threads...")
        for thread in self.bot_channel.threads:
            if thread.owner_id == self.client.user.id:
                await thread.delete()
        logger.info("Completed deleting old theards.")

        logger.info("Deleting old messages...")
        look_until = utcnow() - timedelta(days=365)
        async for msg in self.bot_channel.history(limit=None):
            msg: discord.Message
            if msg.created_at < look_until:
                break
            if msg.author.id == self.client.user.id:
                await msg.delete()
        logger.info("Completed deleting old messages.")

    async def next_task(self):
        task_type = protocol_schema.TaskRequestType.random
        task = self.backend.fetch_task(task_type, user=None)

        handler: task_handlers.ChannelTaskBase = None
        match task.type:
            case TaskType.summarize_story:
                handler = task_handlers.SummarizeStoryHandler()
            case TaskType.rate_summary:
                handler = task_handlers.RateSummaryHandler()
            case TaskType.initial_prompt:
                handler = task_handlers.InitialPromptHandler()
            case TaskType.user_reply:
                handler = task_handlers.UserReplyHandler()
            case TaskType.assistant_reply:
                handler = task_handlers.AssistantReplyHandler()
            case TaskType.rank_initial_prompts:
                handler = task_handlers.RankInitialPromptsHandler()
            case TaskType.rank_user_replies | TaskType.rank_assistant_replies:
                handler = task_handlers.RankConversationsHandler()
            case _:
                logger.warning(f"Unsupported task type received: {task.type}")
                self.backend.nack_task(task.id, "not supported")

        if handler:
            try:
                logger.info(f"strarting task {task.id}")
                msg = await handler.start(self, task)
                self.backend.ack_task(task.id, msg.id)
            except Exception:
                logger.exception("Starting task failed.")
                self.backend.nack_task(task.id, "faled")

    async def background_timer(self):
        next_remove_completed = utcnow() + timedelta(seconds=10)
        next_fetch_task = utcnow() + timedelta(seconds=1)
        while True:
            now = utcnow()

            if self.bot_channel:
                if now > next_fetch_task:
                    next_fetch_task = utcnow() + timedelta(seconds=60)

                    try:
                        await self.next_task()
                    except Exception:
                        logger.exception("fetching next task failed")

            for x in self.reply_handlers.values():
                x.handler.tick(now)

            if now > next_remove_completed:
                next_remove_completed = utcnow() + timedelta(seconds=10)
                await self.remove_completed_handlers()

            await asyncio.sleep(1)

    async def _sync(self, command: str, message: discord.Message):

        logger.info(f"sync tree command received: {command}")

        if command == "sync.copy_global":
            await self.tree.copy_global_to(guild=message.guild)
            synced = await self.tree.sync(guild=message.guild)
        elif command == "sync.clear_guild":
            self.tree.clear_commands(guild=message.guild)
            synced = await self.tree.sync(guild=message.guild)
        elif command == "sync.guild":
            synced = await self.tree.sync(guild=message.guild)
        else:
            synced = await self.tree.sync()

        logger.info(f"Synced {len(synced)} commands")
        await message.reply(f"Synced {len(synced)} commands")

    async def handle_command(self, message: discord.Message, is_owner: bool):
        command_text: str = message.content
        command_text = command_text[1:]
        match command_text:
            case "help" | "?":
                await self.post_help(user=message.author)
            case "sync" | "sync.guild" | "sync.copy_global" | "sync.clear_guild":
                if is_owner:
                    await self._sync(command_text, message)
            case _:
                await message.reply(f"unknown command: {command_text}")

    def recipient_filter(self, message: discord.Message) -> bool:
        channel = message.channel

        if (
            message.channel.type == discord.ChannelType.private
            or message.channel.type == discord.ChannelType.private_thread
        ):
            return True

        if (
            message.channel.type == discord.ChannelType.text
            or message.channel.type == discord.ChannelType.public_thread
        ):
            while channel:
                if self.bot_channel and channel.id == self.bot_channel.id:
                    return True
                channel = channel.parent

        return False

    async def remove_completed_handlers(self):
        completed = [k for k, v in self.reply_handlers.items() if v.handler is None or v.handler.completed]
        if len(completed) == 0:
            return

        for c in completed:
            handler = self.reply_handlers[c]
            del self.reply_handlers[c]
            try:
                await handler.handler.finalize()
            except Exception:
                logger.exception("handler finalize failed")

        logger.info(f"removed {len(completed)} completed handlers (remaining: {len(self.reply_handlers)})")

    def get_text_channel_by_name(self, channel_name) -> discord.TextChannel:
        for channel in self.client.get_all_channels():
            if channel.type == discord.ChannelType.text and channel.name == channel_name:
                return channel

    def run(self):
        """Run bot loop blocking."""
        self.client.run(self.bot_token)
