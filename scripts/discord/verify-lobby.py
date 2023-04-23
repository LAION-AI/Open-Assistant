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
    lobby_channel = await client.fetch_channel("lobby")
    # obtain the role object for the verified role
    verified_role = discord.utils.get(lobby_channel.guild.roles, name="verified")
    async with tqdm.tqdm(lobby_channel.history(limit=None)) as messages:
        async for message in messages:
            if not isinstance(message.author, discord.Member):
                print(f"{message.author} is not a member")
                continue
            if discord.utils.get(message.author.roles, name="unverified"):
                # un-assign the unverified role
                await message.author.remove_roles(verified_role)
                # assign the verified role
                await message.author.add_roles(verified_role)
                print(f"Assigned verified role to {message.author}")
    await client.close()


client.run(settings.bot_token)
