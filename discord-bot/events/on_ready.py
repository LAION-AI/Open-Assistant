from discord.ext.commands import Cog


class OnReady(Cog):
    def __init__(self, client, logger, bot_channel_name):
        self.client = client
        self.logger = logger
        self.bot_channel_name = bot_channel_name
        
    @Cog.listener()
    async def on_ready(self):
        """
        Called when the client is done preparing the data received from Discord.
        Usually after login is successful and the Client.guilds and co. are filled up.
        """
        self.bot_channel = self.get_text_channel_by_name(self.bot_channel_name)
        self.logger.info(f"{self.client.user} is now running!")

        await self.delete_all_old_bot_messages()
        # if self.debug:
        #    await self.post_boot_message()
        await self.post_welcome_message()

        self.client.loop.create_task(self.background_timer(), name="OpenAssistantBot.background_timer()")