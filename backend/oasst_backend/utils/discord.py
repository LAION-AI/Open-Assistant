import requests
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.models.message import Message

ROOT_ENDPOINT = "https://discord.com/api/v10"


def send_new_report_message(
    message: Message,
    label_text: str,
) -> None:
    if settings.DISCORD_API_KEY is None or settings.DISCORD_CHANNEL_ID is None:
        return

    try:
        logger.debug("Sending flagged message to Discord")
        message_text = message.text[:200] + "..." if len(message.text) > 200 else message.text
        label_text = label_text[:200] + "..." if len(label_text) > 200 else label_text
        message_content_embed = {
            "title": "Message content",
            "description": f"{message_text}",
            "color": 0x3498DB,  # Blue
            "footer": {
                "text": f"Role: {message.role.upper()}\t Lang: {message.lang.upper()}\t 👍{message.emojis.get('+1') or 0} 👎{message.emojis.get('-1') or 0} 🚩{message.emojis.get('red_flag') or 0}"
            },
        }
        label_text_embed = {
            "title": "Report content",
            "description": f"{label_text}",
            "color": 0xE74C3C,  # Red
        }
        res = requests.post(
            f"{ROOT_ENDPOINT}/channels/{settings.DISCORD_CHANNEL_ID}/messages",
            headers={
                "authorization": f"Bot {settings.DISCORD_API_KEY}",
            },
            json={
                "content": f"New flagged message https://open-assistant.io/messages/{message.id}",
                "embeds": [message_content_embed, label_text_embed],
            },
        )
        res.raise_for_status()
    except Exception as e:
        logger.exception(f"Failed to send flagged message. error: {e}")
