# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from abc import ABC
from dataclasses import dataclass
from typing import Any

import discord
from api_client import ApiClient
from channel_handlers import ChannelHandlerBase
from loguru import logger
from message_templates import MessageTemplates


@dataclass
class ReplyHandlerInfo:
    msg_id: int
    handler_task: asyncio.Task
    handler: ChannelHandlerBase


class BotBase(ABC):
    bot_channel_name: str
    debug: bool
    backend: ApiClient
    client: discord.Client
    loop: asyncio.BaseEventLoop
    owner_id: int
    bot_channel: discord.TextChannel
    templates: MessageTemplates
    reply_handlers: dict[int, ReplyHandlerInfo]

    def __init__(self):
        self.reply_handlers = {}  # handlers by msg_id

    def ensure_bot_channel(self) -> None:
        if self.bot_channel is None:
            raise RuntimeError(f"bot channel '{self.bot_channel_name}' not found")

    async def post(
        self, content: str, *, view: discord.ui.View = None, channel: discord.abc.Messageable = None
    ) -> discord.Message:
        if channel is None:
            self.ensure_bot_channel()
            channel = self.bot_channel
        return await channel.send(content=content, view=view)

    async def post_template(
        self, name: str, *, view: discord.ui.View = None, channel: discord.abc.Messageable = None, **kwargs: Any
    ) -> discord.Message:
        logger.debug(f"rendering {name}")
        text = self.templates.render(name, **kwargs)
        return await self.post(text, view=view, channel=channel)

    def register_reply_handler(self, msg_id: int, handler: ChannelHandlerBase):
        if msg_id in self.reply_handlers:
            raise RuntimeError(f"Handler already registered for msg_id: {msg_id}")
        task = asyncio.create_task(coro=handler.handler_loop(), name=f"reply_handler(msg_id={msg_id})")
        task.add_done_callback(lambda t: handler.on_completed())
        self.reply_handlers[msg_id] = ReplyHandlerInfo(msg_id=msg_id, handler_task=task, handler=handler)
