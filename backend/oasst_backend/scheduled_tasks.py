from __future__ import absolute_import, unicode_literals

import uuid
from datetime import datetime, timedelta

from celery import shared_task
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.celery_worker import app
from oasst_backend.config import settings
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.task_repository import TaskRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.user_repository import User, UserRepository
from oasst_backend.utils.database_utils import default_session_factory
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.utils import utcnow
from sqlmodel import select

startup_time: datetime = utcnow()


@app.task(name="toxicity")
def toxicity():
    if settings.DEBUG_SKIP_TOXICITY_CALCULATION:
        logger.info("Skipping toxicity calculation")
        return

    logger.info("calculating toxicity")
    with default_session_factory() as session:
        api_key = deps.get_api_key()
        api_client = deps.api_auth(api_key, session)
        pr = PromptRepository(db=session, api_client=api_client)
        tm = TreeManager(db=session, prompt_repository=pr)
        bs = settings.TOXICITY_BATCH_SIZE

        messages = pr.fetch_messages_without_toxicity_score(bs)
        for message in messages:
            try:
                tm.toxicity(message.text, message.id)
            except Exception as e:
                logger.error(
                    f"Could not compute toxicity for text reply to {message.id} with {message.text} by.error {str(e)}"
                )


@app.task(name="hf_feature_extraction")
def hf_feature_extraction():
    if settings.DEBUG_SKIP_EMBEDDING_COMPUTATION:
        logger.info("Skipping embedding computation")
        return

    logger.info("extracting feature embeddings")
    with default_session_factory() as session:
        api_key = deps.get_api_key()
        api_client = deps.api_auth(api_key, session)
        pr = PromptRepository(db=session, api_client=api_client)
        tm = TreeManager(db=session, prompt_repository=pr)
        bs = settings.HF_FEATURE_EXTRACTION_BATCH_SIZE

        messages = pr.fetch_messages_without_embedding(bs)
        for message in messages:
            try:
                tm.hf_feature_extraction(message.text, message.id)
            except Exception as e:
                logger.error(
                    f"Could not extract embedding for text reply to {message.id} with {message.text} by.error {str(e)}"
                )


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
                        # streak_last_day_date has a current timestamp in DB. Ideally should not be NULL.
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


@shared_task(name="complete_pending_ai_tasks")
def complete_pending_ai_tasks() -> None:
    logger.info("complete_pending_ai_tasks start...")
    with default_session_factory() as session:
        db = session
        try:
            api_key = deps.get_api_key()
            api_client = deps.api_auth(api_key, db)
            ur = UserRepository(session, api_client)
            users = ur.get_ai_users()
            for user in users:
                tr = TaskRepository(db, api_client, user, ur)
                tasks = tr.fetch_pending_tasks_of_user(user.id, timedelta(hours=1))
                for task in tasks:
                    pr = PromptRepository(db, api_client, client_user=user)
                    pr.ensure_user_is_enabled()

                    tm = TreeManager(db, pr)
                    output = tm.complete_task(task, user)
                    interaction = protocol_schema.AnyInteraction(
                        **{
                            "user": user,
                            "task_id": task.id,
                            "message_id": task.frontend_message_id,
                            "update_type": "automated",
                            "content": output,
                            "user_message_id": str(uuid.uuid4()),
                            "lang": task.lang,
                        }
                    )
                    _task = tm.handle_interaction(interaction)
                    if type(_task) is protocol_schema.TaskDone:
                        ur.update_user_last_activity(user=pr.user)
            logger.info("complete_ai_pending_tasks end...")
        except Exception as e:
            logger.error(str(e))
