from __future__ import absolute_import, unicode_literals

import os
from datetime import datetime
from typing import Any, Dict, List

from asgiref.sync import async_to_sync
from celery import Celery, shared_task
from dotenv import load_dotenv
from loguru import logger
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.user_repository import User
from oasst_backend.utils.database_utils import default_session_factory
from oasst_backend.utils.hugging_face import HfClassificationModel, HfEmbeddingModel, HfUrl, HuggingFaceAPI
from oasst_shared.utils import utcnow
from sqlmodel import select

result = load_dotenv(".env")
logger.info(f"LoadEnv result {result}")

app = Celery(__name__)
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")
logger.info(f"celery.conf.broker_url {app.conf.broker_url}, app.conf.result_backend{app.conf.result_backend}")
startup_time: datetime = utcnow()

# Load task modules from all registered Django applications.
app.autodiscover_tasks()


@app.task(bind=True)
def info_task(self):
    logger.info("Request: {0!r}".format(self.request))


app.conf.beat_schedule = {
    # Scheduler Name
    "update-user-streak": {
        # Task Name (Name Specified in Decorator)
        "task": "update_user_streak",
        # Schedule
        "schedule": 60.0 * 60.0 * 4,
        # Function Arguments
        # 'args': (10,20)
    },
}


@app.task
def test(arg):
    logger.info(arg)


@app.task(name="create_task")
def create_task(a, b, c):
    # time.sleep(a)
    logger.info(f"IN create task ... {a}")
    return b + c


async def useHFApi(text, url, model_name):
    hugging_face_api: HuggingFaceAPI = HuggingFaceAPI(f"{url}/{model_name}")
    # TODO: This is some wierd error that commenting the next line causes a 400 error
    hugging_face_api.headers: Dict[str, str] = {"Authorization": f"Bearer {hugging_face_api.api_key}"}
    logger.info(f"hf {hugging_face_api.headers}")
    logger.info(f"{str(hugging_face_api)}")
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
            print(f"toxicity from HF {toxicity}")
            api_client_m = ApiClient(**api_client)
            logger.info(f"api_client_m: {api_client_m}")
            print(f"api_client_m: {api_client_m}")
            if toxicity is not None:
                pr = PromptRepository(db=session, api_client=api_client_m)
                pr.insert_toxicity(
                    message_id=message_id, model=model_name, score=toxicity["score"], label=toxicity["label"]
                )

    except Exception as e:
        print(f"Could not compute toxicity for text reply to {message_id=} with {text=} by.error {str(e)}")


@app.task(name="hf_feature_extraction")
def hf_feature_extraction(text, message_id, api_client):
    try:
        with default_session_factory() as session:
            model_name: str = HfEmbeddingModel.MINILM.value
            url: str = HfUrl.HUGGINGFACE_FEATURE_EXTRACTION.value
            embedding = async_to_sync(useHFApi)(text=text, url=url, model_name=model_name)
            logger.info(f"emmbedding from HF {embedding}")
            print(f"emmbedding from HF {embedding}")
            api_client_m = ApiClient(**api_client)
            logger.info(f"api_client_m: {api_client_m}")
            if embedding is not None:
                pr = PromptRepository(db=session, api_client=api_client_m)
                pr.insert_message_embedding(
                    message_id=message_id, model=HfEmbeddingModel.MINILM.value, embedding=embedding
                )

    except Exception as e:
        print(f"Could not extract embedding for text reply to {message_id=} with {text=} by.error {str(e)}")


@shared_task(name="update_user_streak")
def update_user_streak() -> None:
    logger.info("update_user_streak start...")
    try:
        with default_session_factory() as session:
            current_time = utcnow()
            timedelta = current_time - startup_time
            if timedelta.days > 0:
                # Update only greater than 24 hours . Do nothing
                logger.info("Process timedelta greater than 24h")
                statement = select(User)
                result = session.exec(statement).all()
                if result is not None:
                    for user in result:
                        last_activity_date = user.last_activity_date
                        streak_last_day_date = user.streak_last_day_date
                        # set NULL streak_days to 0
                        if user.streak_days is None:
                            user.streak_days = 0
                        # if the user had completed a task
                        if last_activity_date is not None:
                            lastactitvitydelta = current_time - last_activity_date
                            # if the user missed consecutive days of completing a task
                            # reset the streak_days to 0 and set streak_last_day_date to the current_time
                            if lastactitvitydelta.days > 1 or user.streak_days is None:
                                user.streak_days = 0
                                user.streak_last_day_date = current_time
                        # streak_last_day_date has a current timestamp in DB. Idealy should not be NULL.
                        if streak_last_day_date is not None:
                            streak_delta = current_time - streak_last_day_date
                            # if user completed tasks on consecutive days then increment the streak days
                            # update the streak_last_day_date to current time for the next calculation
                            if streak_delta.days > 0:
                                user.streak_days += 1
                                user.streak_last_day_date = current_time
                        session.add(user)
                        session.commit()

            else:
                logger.info("Not yet 24hours since the process started! ...")
        logger.info("User streak end...")
    except Exception as e:
        logger.error(str(e))
    return
