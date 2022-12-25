# -*- coding: utf-8 -*-
from bot import OpenAssistantBot
from bot_settings import settings

# invite bot url: https://discord.com/api/oauth2/authorize?client_id=1054078345542910022&permissions=1634235579456&scope=bot

if __name__ == "__main__":
    bot = OpenAssistantBot(
        settings.BOT_TOKEN,
        bot_channel_name=settings.BOT_CHANNEL_NAME,
        backend_url=settings.BACKEND_URL,
        api_key=settings.API_KEY,
        owner_id=settings.OWNER_ID,
        template_dir=settings.TEMPLATE_DIR,
        debug=settings.DEBUG,
    )
    bot.run()
