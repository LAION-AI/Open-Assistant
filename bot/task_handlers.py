# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import abstractmethod
from datetime import timedelta

import discord
from bot_base import BotBase
from channel_handlers import AutoDestructThreadHandler
from loguru import logger
from oasst_shared.schemas import protocol as protocol_schema
from utils import utcnow


class Questionnaire(discord.ui.Modal, title="Questionnaire Response"):
    name = discord.ui.TextInput(label="Name")
    answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thanks for your response, {self.name}!", ephemeral=True)


class ChannelTaskBase(AutoDestructThreadHandler):
    thread_name: str = "Replies"
    expires_after: timedelta = timedelta(minutes=5)

    async def start(self, bot: BotBase, task: protocol_schema.Task) -> discord.Message:
        self.bot = bot
        self.task = task
        msg = await self.send_first_message()
        self.first_message = msg
        self.thread = await bot.bot_channel.create_thread(message=discord.Object(msg.id), name=self.thread_name)
        await self.on_thread_created(self.thread)
        self.expiry_date = utcnow() + self.expires_after if self.expires_after else None
        bot.register_reply_handler(msg_id=msg.id, handler=self)
        return msg

    async def on_thread_created(self, thread: discord.Thread) -> None:
        pass

    @abstractmethod
    async def send_first_message(self) -> discord.message:
        ...


class SummarizeStoryHandler(ChannelTaskBase):
    task: protocol_schema.SummarizeStoryTask
    thread_name: str = "Summaries"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_summarize_story.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            print("received: ", msg, type(msg))
            logger.info("on_summarize_story_reply")
            await msg.add_reaction("✅")


class InitialPromptHandler(ChannelTaskBase):
    task: protocol_schema.InitialPromptTask
    thread_name: str = "Prompts"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_initial_prompt.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_initial_prompt_reply")
            await msg.add_reaction("✅")


class UserReplyHandler(ChannelTaskBase):
    task: protocol_schema.UserReplyTask
    thread_name: str = "User replies"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_user_reply.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_user_reply_reply")
            await msg.add_reaction("✅")


class AssistantReplyHandler(ChannelTaskBase):
    task: protocol_schema.AssistantReplyTask
    thread_name: str = "Assistant replies"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_assistant_reply.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_assistant_reply_reply")
            await msg.add_reaction("✅")


class RankInitialPromptsHandler(ChannelTaskBase):
    task: protocol_schema.RankInitialPromptsTask
    thread_name: str = "User Responses"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_rank_initial_prompts.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_rank_initial_prompts_reply")
            await msg.add_reaction("✅")


class RankConversationsHandler(ChannelTaskBase):
    task: protocol_schema.RankConversationRepliesTask
    thread_name: str = "Rankings"

    async def send_first_message(self) -> discord.message:
        return await self.bot.post_template("task_rank_conversation_replies.msg", task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_rank_conversation_reply")
            await msg.add_reaction("✅")


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


class RateSummaryHandler(ChannelTaskBase):
    task: protocol_schema.RateSummaryTask
    thread_name: str = "Rate"

    async def _rating_response_handler(self, score, interaction: discord.Interaction):
        logger.info("rating_response_handler", score)
        if self.thread:
            await self.thread.send(f"{interaction.user.name} got your feedback: {score}")
        await interaction.response.send_message(f"got your feedback: {score}")

    async def send_first_message(self) -> discord.message:
        return await self.bot.post("first message")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        view = generate_rating_view(self.task.scale.min, self.task.scale.max, self._rating_response_handler)
        return await self.bot.post_template("task_rate_summary.msg", view=view, channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info("on_rate_summary_reply")
            await msg.add_reaction("✅")
