# -*- coding: utf-8 -*-
import asyncio
from typing import Any

import discord
from api_client import ApiClient, TaskType
from schemas import protocol as protocol_schema


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


class ModifiedClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: Any):
        super().__init__(intents=intents, **options)

    async def setup_hook(self):
        print("setup")


class OpenAssistantBot:
    def __init__(self, bot_token: str, bot_channel_name: str, backend_url: str, api_key: str):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot_token = bot_token
        client = ModifiedClient(intents=intents)
        self.client = client
        self.bot_channel: discord.TextChannel = None
        self.backend = ApiClient(backend_url, api_key)
        self.reply_handlers = {}  # handlers by msg_id

        @client.event
        async def on_ready():
            self.bot_channel = self.get_text_channel_by_name(bot_channel_name)

            client.loop.create_task(self.background_timer(), name="OpenAssistantBot.background_timer()")
            print(f"{client.user} is now running!")

        @client.event
        async def on_message(message: discord.Message):
            # ignore own messages
            if message.author == client.user:
                return

            await self.handle_message(message)

    async def generate_summarize_story(self, task: protocol_schema.SummarizeStoryTask):
        text = f"Summarize to the following story:\n{task.story}"
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_summarize_story_reply", message)
            await message.reply("thx, on_summarize_story_reply")

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
            print("rating_response_handler", score)
            await interaction.response.send_message(f"got your feedback: {score}")

        view = generate_rating_view(task.scale.min, task.scale.max, rating_response_handler)
        msg: discord.Message = await self.bot_channel.send(text, view=view)

        async def on_reply(message: discord.Message):
            print("on_summary_reply", message)
            await message.reply("thx, on_summary_reply")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_initial_prompt(self, task: protocol_schema.InitialPromptTask):
        text = "Please provide an initial prompt to the assistant."
        if task.hint:
            text += f"\nHint: {task.hint}"
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_initial_prompt_reply", message)
            await message.reply("thx, on_initial_prompt_reply")

        self.reply_handlers[msg.id] = on_reply

        return msg

    def _render_message(self, message: protocol_schema.ConversationMessage) -> str:
        """Render a message to the user."""
        if message.is_assistant:
            return f"Assistant: {message.text}"
        return f"User: {message.text}"

    async def generate_user_reply(self, task: protocol_schema.UserReplyTask):
        s = ["Please provide a reply to the assistant.", "Here is the conversation so far:"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
        if task.hint:
            s.append(f"Hint: {task.hint}")
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_user_reply_reply", message)
            await message.reply("thx, on_user_reply_reply")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_assistant_reply(self, task: protocol_schema.AssistantReplyTask):
        s = ["Act as the assistant and reply to the user.", "Here is the conversation so far:"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_assistant_reply_reply", message)
            await message.reply("thx, on_assistant_reply_reply")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_rank_initial_prompts(self, task: protocol_schema.RankInitialPromptsTask):
        s = ["Rank the following prompts:"]
        for idx, prompt in enumerate(task.prompts, start=1):
            s.append(f"{idx}: {prompt}")
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_rank_initial_prompts_reply", message)
            await message.reply("thx, on_rank_initial_prompts_reply")

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def generate_rank_conversation(self, task: protocol_schema.RankConversationRepliesTask):
        s = ["Here is the conversation so far:"]
        for message in task.conversation.messages:
            s.append(self._render_message(message))
        s.append("Rank the following replies:")
        for idx, reply in enumerate(task.replies, start=1):
            s.append(f"{idx}: {reply}")
        text = "\n".join(s)
        msg: discord.Message = await self.bot_channel.send(text)

        async def on_reply(message: discord.Message):
            print("on_rrank_conversation_reply", message)
            message

        self.reply_handlers[msg.id] = on_reply

        return msg

    async def next_task(self):
        task = self.backend.fetch_task(protocol_schema.TaskRequestType.rate_summary, user=None)
        # task = self.backend.fetch_random_task(user=None)

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
            await self.backend.ack_task(task.id, msg.id)
        else:
            await self.backend.nack_task(task.id, "not supported")

    async def background_timer(self):
        while True:
            if self.bot_channel:
                try:
                    await self.next_task()
                except Exception as e:
                    print(e)
            await asyncio.sleep(30)

    def run(self):
        """Run bot loop blocking."""
        self.client.run(self.bot_token)

    async def handle_message(self, message: discord.Message):
        user_id = message.author.id
        user_display_name = message.author.name

        if message.reference:
            handler = self.reply_handlers.get(message.reference.message_id)
            if handler:
                await handler(message)

        print(user_id, user_display_name, message.content, type(message.content))

    def get_text_channel_by_name(self, channel_name) -> discord.TextChannel:
        for channel in self.client.get_all_channels():
            if channel.type == discord.ChannelType.text and channel.name == channel_name:
                return channel
