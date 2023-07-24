from uuid import UUID

import requests
from loguru import logger
from oasst_backend.celery_worker import app as celery_app
from oasst_backend.config import settings

ROOT_ENDPOINT = "https://discord.com/api/v10"


@celery_app.task(name="send_new_report_message")
def send_new_report_message(message_details: dict, label_text: str, user_id: UUID):
    """
    Send a message to the Discord channel when a new message is flagged.
    Note: this is a Celery task.

    Args:
        message_details (dict): some of the attributes of a Message instance that we will use to compose the discord
        message.
        label_text (str): the label text
        user_id (UUID): the user ID
    """
    if settings.DISCORD_API_KEY is None or settings.DISCORD_CHANNEL_ID is None:
        return

    try:
        logger.debug("Sending flagged message to Discord")
        label_text = label_text[:4096]  # 4096 is the max length of discord embed description
        message_content_embed = {
            "title": "Message content",
            "description": message_details["message_text"],
            "color": 0x3498DB,  # Blue
            "footer": {
                "text": (
                    f"Role: {message_details['role']}\t "
                    f"Lang: {message_details['lang']}\t "
                    f"👍{message_details['thumbs_up']} "
                    f"👎{message_details['thumbs_down']} "
                    f"🚩{message_details['red_flag']}"
                )
            },
        }
        label_text_embed = {
            "title": "Report content",
            "description": f"{label_text}",
            "color": 0xE74C3C,  # Red
            "author": {
                "name": f"User ID: {user_id}",
                "url": f"https://open-assistant.io/admin/manage_user/{user_id}",
            },
        }
        res = requests.post(
            f"{ROOT_ENDPOINT}/channels/{settings.DISCORD_CHANNEL_ID}/messages",
            headers={
                "user-agent": "DiscordBot (https://open-assistant.io, 1)",
                "authorization": f"Bot {settings.DISCORD_API_KEY}",
            },
            json={
                "content": f"New flagged message https://open-assistant.io/admin/messages/{message_details['message_id']}",
                "embeds": [message_content_embed, label_text_embed],
            },
        )
        res.raise_for_status()
    except Exception as e:
        logger.exception(f"Failed to send flagged message. error: {e}")
