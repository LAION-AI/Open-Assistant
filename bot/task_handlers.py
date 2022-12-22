# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import abstractmethod
from datetime import timedelta

import discord
from api_client import ApiClient
from bot_base import BotBase
from channel_handlers import AutoDestructThreadHandler, ChannelExpiredException
from loguru import logger
from oasst_shared.schemas import protocol as protocol_schema
from utils import DiscordTimestampStyle, discord_timestamp, utcnow


class Questionnaire(discord.ui.Modal, title="Questionnaire Response"):
    name = discord.ui.TextInput(label="Name")
    answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thanks for your response, {self.name}!", ephemeral=True)


class ChannelTaskBase(AutoDestructThreadHandler):
    thread_name: str = "Replies"
    expires_after: timedelta = timedelta(minutes=5)
    backend: ApiClient

    async def start(self, bot: BotBase, task: protocol_schema.Task) -> discord.Message:
        try:
            self.bot = bot
            self.task = task
            self.backend = bot.backend
            self.expiry_date = utcnow() + self.expires_after if self.expires_after else None
            msg = await self.send_first_message()
            self.first_message = msg
            self.thread = await bot.bot_channel.create_thread(message=discord.Object(msg.id), name=self.thread_name)
            await self.on_thread_created(self.thread)
        except Exception:
            logger.exception("start task failed")
            await self.cleanup()  # try to cleanup messag or thread
            raise

        bot.register_reply_handler(msg_id=msg.id, handler=self)
        return msg

    async def on_thread_created(self, thread: discord.Thread) -> None:
        pass

    @abstractmethod
    async def send_first_message(self) -> discord.message:
        ...

    def to_api_user(self, user: discord.User) -> protocol_schema.User:
        return protocol_schema.User(auth_method="discord", id=user.id, display_name=user.display_name)

    async def post_teaser_msg(self, template_name: str):
        expiry_time = discord_timestamp(self.expiry_date, DiscordTimestampStyle.long_time)
        expiry_relatve = discord_timestamp(self.expiry_date, DiscordTimestampStyle.relative_time)
        return await self.bot.post_template(
            template_name, task=self.task, expiry_time=expiry_time, expiry_relatve=expiry_relatve
        )

    async def post_interaction(self, interaction: protocol_schema.Interaction) -> protocol_schema.Task:
        api_response = await self.backend.post_interaction(interaction)
        if api_response.type != "task_done":
            # multi-step tasks are not supported yet
            logger.error(f"multi-step tasks are not supported yet (got response type: {api_response.type})")
            raise RuntimeError("Unexpected response from backend received")
        return api_response

    def post_text_reply_to_post(self, user_msg: discord.Message) -> protocol_schema.Task:
        return self.backend.post_interaction(
            protocol_schema.TextReplyToPost(
                post_id=str(self.first_message.id),
                user_post_id=str(user_msg.id),
                user=self.to_api_user(user_msg.author),
                text=user_msg.content,
            )
        )

    async def handle_text_reply_to_post(self, user_msg: discord.Message) -> protocol_schema.Task:
        try:
            self.post_text_reply_to_post(user_msg)
            await user_msg.add_reaction("✅")
        except ChannelExpiredException:
            raise
        except Exception as e:
            logger.exception("Error in handle_text_reply_to_post()")
            await user_msg.add_reaction("❌")
            await user_msg.reply(f"❌ Error communicating with backend: {e}")

    def post_ranking(self, user_msg: discord.Message, ranking: list[int]) -> protocol_schema.Task:
        return self.backend.post_interaction(
            protocol_schema.PostRanking(
                post_id=str(self.first_message.id),
                user_post_id=str(user_msg.id),
                user=self.to_api_user(user_msg.author),
                ranking=ranking,
            )
        )

    async def handle_ranking(self, user_msg: discord.Message) -> protocol_schema.Task:
        try:
            ranking_str = user_msg.content
            ranking = [int(x) - 1 for x in ranking_str.split(",")]
            self.post_ranking(user_msg, ranking=ranking)
            await user_msg.add_reaction("✅")
        except ChannelExpiredException:
            raise
        except Exception as e:
            logger.exception("Error in handle_ranking()")
            await user_msg.add_reaction("❌")
            await user_msg.reply(f"❌ Error communicating with backend: {e}")


class SummarizeStoryHandler(ChannelTaskBase):
    task: protocol_schema.SummarizeStoryTask
    thread_name: str = "Summaries"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_summarize_story.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_summarize_story.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_text_reply_to_post(msg)


class InitialPromptHandler(ChannelTaskBase):
    task: protocol_schema.InitialPromptTask
    thread_name: str = "Prompts"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_initial_prompt.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_initial_prompt.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_text_reply_to_post(msg)


class UserReplyHandler(ChannelTaskBase):
    task: protocol_schema.UserReplyTask
    thread_name: str = "User replies"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_user_reply.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_user_reply.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_text_reply_to_post(msg)


class AssistantReplyHandler(ChannelTaskBase):
    task: protocol_schema.AssistantReplyTask
    thread_name: str = "Assistant replies"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_assistant_reply.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_assistant_reply.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_text_reply_to_post(msg)


class RankInitialPromptsHandler(ChannelTaskBase):
    task: protocol_schema.RankInitialPromptsTask
    thread_name: str = "User Responses"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_rank_initial_prompts.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_rank_initial_prompts.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_ranking(msg)


class RankConversationsHandler(ChannelTaskBase):
    task: protocol_schema.RankConversationRepliesTask
    thread_name: str = "Rankings"

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_rank_conversation_replies.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        await self.bot.post_template("task_rank_conversation_replies.msg", channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            await self.handle_ranking(msg)


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
    thread_name: str = "Ratings"

    async def _rating_response_handler(self, score, interaction: discord.Interaction):
        logger.info("rating_response_handler", score)
        if self.thread:
            try:
                self.backend.post_interaction(
                    protocol_schema.PostRating(
                        post_id=str(self.first_message.id),
                        user_post_id=str(interaction.id),
                        user=self.to_api_user(interaction.user),
                        rating=score,
                    )
                )
                await interaction.response.send_message(
                    f"Thanks {interaction.user.display_name}, got your feedback: {score}!"
                )
            except ChannelExpiredException:
                raise
            except Exception as e:
                logger.exception("Error in _rating_response_handler()")
                interaction.response.send_message(f"❌ Error communicating with backend: {e}")

    async def send_first_message(self) -> discord.message:
        return await self.post_teaser_msg("teaser_rate_summary.msg")

    async def on_thread_created(self, thread: discord.Thread) -> None:
        view = generate_rating_view(self.task.scale.min, self.task.scale.max, self._rating_response_handler)
        return await self.bot.post_template("task_rate_summary.msg", view=view, channel=thread, task=self.task)

    async def handler_loop(self):
        while True:
            msg = await self.read()
            logger.info(f"on_rate_summary_reply: {msg.content}")
            await msg.add_reaction("❌")
            await msg.reply("❌ Text intput not supported.")
