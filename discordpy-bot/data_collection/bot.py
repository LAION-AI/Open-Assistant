from discord.ext import commands
from dotenv import load_dotenv

import discord
import asyncio
import os


class DataCollectionBot(commands.AutoShardedBot):
    '''
    A bot for collecting data from the Discord API.
    '''

    def __init__(self, *args, **kwargs):
        print('Initializing DataCollectionBot...')


        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        self.remove_command('help')

        for filename in os.listdir(os.path.dirname(__file__)+'/cogs/commands'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.commands.{filename[:-3]}')

        for filename in os.listdir(os.path.dirname(__file__)+'/cogs/events'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.events.{filename[:-3]}')


async def main():
    load_dotenv()

    intents = discord.Intents.all()
    intents.presences = False

    bot = DataCollectionBot(        
        command_prefix=os.getenv('PREFIX'),
        intents=intents,
        debug_guild=os.getenv('DECLARE_GLOBAL_COMMANDS'),
        owner_id=os.getenv('OWNER_ID'),
    )

    await bot.start(os.getenv('BOT_TOKEN'))


asyncio.run(main())