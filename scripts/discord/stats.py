#!/usr/bin/env python3

"""This file is for moderators to verify new users in the lobby.

First, moderators read the brief introduction people write in the lobby.
If all people's introductions are acceptable, moderators run this script.

Needs BOT_TOKEN environment variable to be set to the bot token.

"""


import discord
import pydantic
import tqdm.asyncio as tqdm


class Settings(pydantic.BaseSettings):
    bot_token: str


settings = Settings()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    lobby_channel = discord.utils.get(client.get_all_channels(), name="lobby")
    message: discord.Message
    times = []
    async for message in tqdm.tqdm(lobby_channel.history(limit=None)):
        times.append(message.created_at.timestamp())
    with open("times.txt", "w") as f:
        f.write("\n".join(map(str, times)))
    await client.close()


client.run(settings.bot_token)
