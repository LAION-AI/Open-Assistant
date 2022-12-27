from discord.ext.commands import Cog
from discord import Message, MessageType, Thread

class OnMessage(Cog):
    def __init__(self, client, logger):
        self.client = client
        self.logger = logger

    @Cog.listener()
    async def on_message(self, message):
        """ Called when a message is sent to a channel the bot has access to. """
        # ignore own messages
        if message.author != self.client.user:
            await self.handle_message(message)
            
    async def handle_message(self, message: Message):
        if not self.recipient_filter(message):
            return

        user_id = message.author.id
        user_display_name = message.author.name

        self.logger.debug(
            f"{message.type} {message.channel.type} from ({user_display_name}) {user_id}: {message.content} ({type(message.content)})"
        )

        command_prefix = "!"
        if message.type == MessageType.default and message.content.startswith(command_prefix):
            is_owner = self.owner_id and user_id == self.owner_id
            await self.handle_command(message, is_owner)

        if isinstance(message.channel, Thread):
            handler = self.reply_handlers.get(message.channel.id)
            if handler and not handler.handler.completed:
                handler.handler.on_reply(message)

        if message.reference:
            handler = self.reply_handlers.get(message.reference.message_id)
            if handler and not handler.handler.completed:
                handler.handler.on_reply(message)