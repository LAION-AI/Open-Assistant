from __future__ import absolute_import, unicode_literals

from datetime import datetime
from typing import Any, Dict, List

from asgiref.sync import async_to_sync
from celery import shared_task
from loguru import logger
from oasst_backend.celery_worker import app
from oasst_backend.models import ApiClient, Message
from oasst_backend.models.db_payload import MessagePayload
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.utils.database_utils import db_lang_to_postgres_ts_lang, default_session_factory
from oasst_backend.utils.hugging_face import HfClassificationModel, HfEmbeddingModel, HfUrl, HuggingFaceAPI
from oasst_shared.utils import utcnow
from sqlalchemy import func

startup_time: datetime = utcnow()


async def useHFApi(text, url, model_name):
    hugging_face_api: HuggingFaceAPI = HuggingFaceAPI(f"{url}/{model_name}")
    result = await hugging_face_api.post(text)
    return result


@app.task(name="toxicity")
def toxicity(text, message_id, api_client):
    try:
        logger.info(f"checking toxicity : {api_client}")

        with default_session_factory() as session:
            model_name: str = HfClassificationModel.TOXIC_ROBERTA.value
            url: str = HfUrl.HUGGINGFACE_TOXIC_CLASSIFICATION.value
            toxicity: List[List[Dict[str, Any]]] = async_to_sync(useHFApi)(text=text, url=url, model_name=model_name)
            toxicity = toxicity[0][0]
            logger.info(f"toxicity from HF {toxicity}")
            api_client_m = ApiClient(**api_client)
            if toxicity is not None:
                pr = PromptRepository(db=session, api_client=api_client_m)
                pr.insert_toxicity(
                    message_id=message_id, model=model_name, score=toxicity["score"], label=toxicity["label"]
                )
            session.commit()

    except Exception as e:
        logger.error(f"Could not compute toxicity for text reply to {message_id=} with {text=} by.error {str(e)}")


@app.task(name="hf_feature_extraction")
def hf_feature_extraction(text, message_id, api_client):
    try:
        with default_session_factory() as session:
            model_name: str = HfEmbeddingModel.MINILM.value
            url: str = HfUrl.HUGGINGFACE_FEATURE_EXTRACTION.value
            embedding = async_to_sync(useHFApi)(text=text, url=url, model_name=model_name)
            api_client_m = ApiClient(**api_client)
            if embedding is not None:
                logger.info(f"emmbedding from HF {len(embedding)}")
                pr = PromptRepository(db=session, api_client=api_client_m)
                pr.insert_message_embedding(
                    message_id=message_id, model=HfEmbeddingModel.MINILM.value, embedding=embedding
                )
                session.commit()

    except Exception as e:
        logger.error(f"Could not extract embedding for text reply to {message_id=} with {text=} by.error {str(e)}")


@shared_task(name="update_search_vectors")
def update_search_vectors(batch_size: int) -> None:
    logger.info("update_search_vectors start...")
    try:
        with default_session_factory() as session:
            while True:
                to_update: list[Message] = (
                    session.query(Message).filter(Message.search_vector.is_(None)).limit(batch_size).all()
                )

                if not to_update:
                    break

                for message in to_update:
                    message_payload: MessagePayload = message.payload.payload
                    message_lang: str = db_lang_to_postgres_ts_lang(message.lang)
                    message.search_vector = func.to_tsvector(message_lang, message_payload.text)

                session.commit()
    except Exception as e:
        logger.error(f"update_search_vectors failed with error: {str(e)}")


@shared_task(name="update_user_streak")
def update_user_streak() -> None:
    # check if user has been active in the last 24h and update streak accordingly
    logger.info("update_user_streak start...")
    try:
        with default_session_factory() as session:
            current_time = utcnow()
            logger.info("Process timedelta greater than 24h")

            # Reset streak_days to 0 for users with more than one day of inactivity
            reset_query = f"""
                    UPDATE "user"
                    SET streak_days = 0,
                        streak_last_day_date = '{current_time}'
                    WHERE ('{current_time}' - last_activity_date) > interval '1 day'
                        OR streak_days IS NULL
                        OR last_activity_date IS NULL
                """
            session.execute(reset_query)
            session.commit()

        logger.info("User streak reset successfully!")
    except Exception as e:
        logger.error(str(e))
