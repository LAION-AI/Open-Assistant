from discord.ext import commands
import discord


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Ready.')

        self.tree.copy_global_to(guild=discord.Object(self.debug_guild))
        await self.tree.sync()
        await self.bot.change_presence(activity=discord.Game(name=f'/help -Collect data!'))


async def setup(bot):
    await bot.add_cog(Ready(bot))
