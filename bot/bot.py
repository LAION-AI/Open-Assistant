# -*- coding: utf-8 -*-
import asyncio
from typing import Optional, Union

import discord
from api_client import ApiClient, TaskType
from discord import app_commands
from loguru import logger
from oasst_shared.schemas import protocol as protocol_schema


class RatingButton(discord.ui.Button):
    def __init__(self, label, value, response_handler):
        super().__init__(label=label, style=discord.ButtonStyle.green)
        self.value = value
        self.response_handler = response_handler

    async def callback(self, interaction):
        await self.response_handler(self.value, interaction)


def generate_rating_view(lo: int, hi: int, response_handler) -> discord.ui.View:
    view = discord.ui.View()
    for i in range(lo, hi + 1):
        view.add_item(RatingButton(str(i), i, response_handler))
    return view


class OpenAssistantBot:
    def __init__(
        self,
        bot_token: str,
        bot_channel_name: str,
        backend_url: str,
        api_key: str,
        owner_id: Optional[Union[int, str]] = None,
    ):
        intents = discord.Intents.default()
        intents.message_content = True

        if isinstance(owner_id, str):
            owner_id = int(owner_id)
        self.owner_id = owner_id

        self.bot_token = bot_token
        client = discord.Client(intents=intents)
        self.client = client

        self.bot_channel: discord.TextChannel = None
        self.backend = ApiClient(backend_url, api_key)
        self.reply_handlers = {}  # handlers by msg_id
        self.tree = app_commands.CommandTree(self.client, fallback_to_global=True)

        self.auto_archive_minutes = 60  # ToDo: add to bot config

        @client.event
        async def on_ready():
            self.bot_channel = self.get_text_channel_by_name(bot_channel_name)
            client.loop.create_task(self.background_timer(), name="OpenAssistantBot.background_timer()")
            logger.info(f"{client.user} is now running!")

        @client.event
        async def on_message(message: discord.Message):
            # ignore own messages
            if message.author != client.user:
                await self.handle_message(message)

        @self.tree.command()
        async def tutorial(interaction: discord.Interaction):
            """Start the Open-Assistant tutorial via DMs."""
            await interaction.response.send_message(f"tutorial command by {interaction.user.name}")

        @self.tree.command()
        async def help(interaction: discord.Interaction):
            """Sends the user a list of all available commands"""
            await interaction.response.send_message(f"help command by {interaction.user.name}")

        @self.tree.command()
        async def work(interaction: discord.Interaction):
            """Request a new personalized task"""
            await interaction.response.send_message(f"work command by {interaction.user.name}")

    async def print_separtor(self, title: str) -> discord.Message:
        msg: discord.Message = await self.bot_channel.send(f"\n:point_right:  {title}  :point_left:\n")
        return msg

    async def generate_summarize_story(self, task: protocol_schema.SummarizeStoryTask):
        text = f"Summarize to the following story:\n{task.story}"
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="Summaries", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_summarize_story_reply", message)
            await message.add_reaction("✅")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_rate_summary(self, task: protocol_schema.RateSummaryTask):
        s = [
            "Rate the following summary:",
            task.summary,
            "Full text:",
            task.full_text,
            f"Rating scale: {task.scale.min} - {task.scale.max}",
        ]
        text = "\n".join(s)

        async def rating_response_handler(score, interaction: discord.Interaction):
            logger.info("rating_response_handler", score)
            await interaction.response.send_message(f"got your feedback: {score}")

        view = generate_rating_view(task.scale.min, task.scale.max, rating_response_handler)
        msg: discord.Message = await self.bot_channel.send(text, view=view)

        async def on_reply(message: discord.Message):
            logger.info("on_summary_reply", message)
            await message.add_reaction("")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_initial_prompt(self, task: protocol_schema.InitialPromptTask):
        text = "Please provide an initial prompt to the assistant."
        if task.hint:
            text += f"\nHint: {task.hint}"
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="Prompts", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_initial_prompt_reply", message)
            await message.add_reaction("✅")

        self.reply_handlers[msg.id] = on_reply

        return msg

    def _render_message(self, message: protocol_schema.ConversationMessage) -> str:
        """Render a message to the user."""
        if message.is_assistant:
            return f":robot: Assistant:\n{message.text}"
        else:
            return f":person_red_hair: User:\n**{message.text}**"

    async def generate_user_reply(self, task: protocol_schema.UserReplyTask):
        s = ["Please provide a reply to the assistant.", "Here is the conversation so far:\n"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
            s.append("")
        if task.hint:
            s.append(f"Hint: {task.hint}")
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="User responses", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_user_reply_reply", message)
            await message.add_reaction("✅")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_assistant_reply(self, task: protocol_schema.AssistantReplyTask):
        s = ["Act as the assistant and reply to the user.", "Here is the conversation so far\n:"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
            s.append("")
        s.append(":robot: Assistant: { human, pls help me! ... }")
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="Agent responses", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_assistant_reply_reply", message)
            await message.add_reaction("✅")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_rank_initial_prompts(self, task: protocol_schema.RankInitialPromptsTask):
        s = ["Rank the following prompts:"]
        for idx, prompt in enumerate(task.prompts, start=1):
            s.append(f"{idx}: {prompt}")
        s.append("")
        s.append(':scroll: Reply with the numbers of best to worst prompts separated by commas (example: "4,1,3,2").')
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="User responses", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_rank_initial_prompts_reply", message)
            await message.add_reaction("✅")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_rank_conversation(self, task: protocol_schema.RankConversationRepliesTask):
        s = ["Here is the conversation so far:"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
        s.append("")
        s.append("Rank the following replies:")
        for idx, reply in enumerate(task.replies, start=1):
            s.append(f"{idx}: {reply}")
        s.append("")
        s.append(':scroll: Reply with the numbers of best to worst prompts separated by commas (example: "4,1,3,2").')
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)
        await self.bot_channel.create_thread(
            message=discord.Object(msg.id), name="User responses", auto_archive_duration=self.auto_archive_minutes
        )

        async def on_reply(message: discord.Message):
            logger.info("on_rank_conversation_reply", message)
            await message.add_reaction("✅")
            message

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def next_task(self):
        # task = self.backend.fetch_task(protocol_schema.TaskRequestType.user_reply, user=None)
        task = self.backend.fetch_random_task(user=None)

        await self.print_separtor("New Task")

        msg: discord.Message = None
        match task.type:
            case TaskType.summarize_story:
                msg = await self.generate_summarize_story(task)
            case TaskType.rate_summary:
                msg = await self.generate_rate_summary(task)
            case TaskType.initial_prompt:
                msg = await self.generate_initial_prompt(task)
            case TaskType.user_reply:
                msg = await self.generate_user_reply(task)
            case TaskType.assistant_reply:
                msg = await self.generate_assistant_reply(task)
            case TaskType.rank_initial_prompts:
                msg = await self.generate_rank_initial_prompts(task)
            case TaskType.rank_user_replies | TaskType.rank_assistant_replies:
                msg = await self.generate_rank_conversation(task)

        if msg is not None:
            self.backend.ack_task(task.id, msg.id)
        else:
            self.backend.nack_task(task.id, "not supported")

    async def background_timer(self):
        while True:
            if self.bot_channel:
                try:
                    await self.next_task()
                except Exception:
                    logger.exception("fetching next task failed")
            await asyncio.sleep(30)

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
            case "sync" | "sync.guild" | "sync.copy_global" | "sync.clear_guild" | "sync.clear_guild":
                if is_owner:
                    await self._sync(command_text, message)
            case _:
                await message.reply(f"unknown command: {command_text}")

    async def handle_message(self, message: discord.Message):
        user_id = message.author.id
        user_display_name = message.author.name

        command_prefix = "!"
        if (
            message.channel.type == discord.ChannelType.private
            and message.type == discord.MessageType.default
            and message.content.startswith(command_prefix)
        ):
            is_owner = self.owner_id and user_id == self.owner_id
            await self.handle_command(message, is_owner)

        if isinstance(message.channel, discord.Thread):
            handler = self.reply_handlers.get(message.channel.id)
            if handler:
                await handler(message)

        if message.reference:
            handler = self.reply_handlers.get(message.reference.message_id)
            if handler:
                await handler(message)

        logger.debug(
            f"{message.type} {message.channel.type} from ({user_display_name}) {user_id}: {message.content} ({type(message.content)})"
        )

    def get_text_channel_by_name(self, channel_name) -> discord.TextChannel:
        for channel in self.client.get_all_channels():
            if channel.type == discord.ChannelType.text and channel.name == channel_name:
                return channel

    def run(self):
        """Run bot loop blocking."""
        self.client.run(self.bot_token)
