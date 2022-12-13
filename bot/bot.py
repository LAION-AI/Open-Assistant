# -*- coding: utf-8 -*-

import json
import os

import discord
import requests
from discord import app_commands
from dotenv import load_dotenv

bot_url = "https://discord.com/api/oauth2/authorize?client_id=1051614245940375683&permissions=8&scope=bot"

# Load up all the important environment variables.
load_dotenv()

# For authentication.
TOKEN = os.getenv("DISCORD_TOKEN")

# For Backends.
API_SERVER_URL = os.getenv("API_SERVER_URL")
API_SERVER_KEY = os.getenv("API_SERVER_KEY")

labelers_url = f"{API_SERVER_URL}/api/v1/labelers/"
prompts_url = f"{API_SERVER_URL}/api/v1/prompts/"
headers = {"X-API-Key": API_SERVER_KEY}

# For testing only.
TEST_GUILD = os.getenv("TEST_GUILD")


# Initiate the client and command tree to create slash commands.
class OpenChatGPTClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if TEST_GUILD:
            # When testing the bot it's handy to run in a single server (called a
            # Guide in the API).  This is relatively fast.
            guild = discord.Object(id=TEST_GUILD)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            # This can take up to an hour for the commands to be registered.
            await self.tree.sync()
        print("Ready!")


# List the set of intents needed for commands to operate properly.
intents = discord.Intents.default()
intents.message_content = True
client = OpenChatGPTClient(intents=intents)


@client.tree.command()
async def register(interaction: discord.Interaction):
    """Registers the user for submissions."""
    labeler = {
        "discord_username": f"{interaction.user.id}",
        "display_name": interaction.user.name,
        "is_enabled": True,
    }
    response = requests.post(labelers_url, headers=headers, json=labeler)
    if response.status_code == 200:
        await interaction.response.send_message(f"Added you {interaction.user.name}")
    else:
        print(response)
        await interaction.response.send_message("Failed to add you")


@client.tree.command()
async def list_participants(interaction: discord.Interaction):
    """Reports the set of registered participants."""
    response = requests.get(labelers_url, headers=headers)
    if response.status_code == 200:
        names = ",".join([labeler["display_name"] for labeler in response.json()])
        await interaction.response.send_message(f"Found these users: {names}")
    else:
        await interaction.response.send_message("Failed to fetch participants")


@client.tree.command()
async def add_prompt(interaction: discord.Interaction, prompt: str, response: str, language: str = "en"):
    """Uploads a single prompt to the server."""
    prompt = {
        "discord_username": f"{interaction.user.id}",
        "labeler_id": 5,
        "prompt": prompt,
        "response": response,
        "lang": language,
    }
    response = requests.post(prompts_url, headers=headers, json=prompt)
    if response.status_code == 200:
        await interaction.response.send_message("Added your prompt")
    else:
        await interaction.response.send_message("Failed to add the prompt")


@client.tree.command()
async def add_prompts_set(interaction: discord.Interaction, prompts: discord.Attachment):
    """Uploads a batch of prompts to the server."""
    # Loading a bunch of prompts from a file can take a while.  So first defer
    # the response to ensure we're able to later tell the user what happened.
    await interaction.response.defer(ephemeral=True)

    # Read the prompts and load them one by one.
    # TODO: Upload a batch when the API supports it.
    # TODO: Handle incorrect file types and parsing errors.
    prompts_raw = await prompts.read()
    prompts_loaded = json.loads(prompts_raw)
    count = 0
    for entry in prompts_loaded:
        for response in entry["responses"]:
            prompt = {
                "discord_username": f"{interaction.user.id}",
                "labeler_id": 5,
                "prompt": entry["prompt"],
                "response": response,
                "lang": "en",
            }
            response = requests.post(prompts_url, headers=headers, json=prompt)
            if response.status_code != 200:
                await interaction.followup.send("Failed to upload")
                return
            count += 1
    await interaction.followup.send(f"Loaded up {count} prompts")


client.run(TOKEN)
