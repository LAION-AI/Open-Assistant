import time

from loguru import logger
from oasst_backend.models import ApiClient, Message
from oasst_backend.scheduled_tasks import hf_feature_extraction, toxicity
from oasst_backend.utils.database_utils import default_session_factory
from sqlmodel import text


def get_messageids_without_toxicity():
    message_ids = None
    with default_session_factory() as session:
        sql = """
        SELECT m.id FROM message as m
        left join message_toxicity mt on mt.message_id = m.id
        where mt.message_id is NULL
        """
        result = session.execute(
            text(sql),
        ).all()
        message_ids = []
        for row in result:
            message_id = row[0]
            message_ids.append(message_id)
    return message_ids


def get_messageids_without_embedding():
    message_ids = None
    with default_session_factory() as session:
        sql = """
        SELECT m.id FROM message as m
        left join message_embedding mt on mt.message_id = m.id
        where mt.message_id is NULL
        """
        result = session.execute(
            text(sql),
        ).all()
        message_ids = []
        for row in result:
            message_id = row[0]
            message_ids.append(message_id)
    return message_ids


def find_and_update_embeddings(message_ids):
    try:
        with default_session_factory() as session:
            for message_id in message_ids:
                result = session.query(Message).filter(Message.id == message_id).first()
                if result is not None:
                    api_client_id = result.api_client_id
                    text = result.payload.payload.text
                    api_client = session.query(ApiClient).filter(ApiClient.id == api_client_id).first()
                    if api_client is not None and text is not None:
                        hf_feature_extraction(text=text, message_id=message_id, api_client=api_client.__dict__)
                        # to not get rate limited from HF
                        time.sleep(10)
    except Exception as e:
        logger.error(str(e))
    logger.debug("Done: find_and_update_embeddings")


def find_and_update_toxicity(message_ids):
    try:
        with default_session_factory() as session:
            for message_id in message_ids:
                result = session.query(Message).filter(Message.id == message_id).first()
                if result is not None:
                    api_client_id = result.api_client_id
                    text = result.payload.payload.text
                    api_client = session.query(ApiClient).filter(ApiClient.id == api_client_id).first()
                    if api_client is not None and text is not None:
                        toxicity(text=text, message_id=message_id, api_client=api_client.__dict__)
                        # to not get rate limited from HF
                        time.sleep(10)
    except Exception as e:
        logger.error(str(e))
    logger.debug("Done:  find_and_update_toxicity")


def main():
    message_ids = get_messageids_without_toxicity()
    find_and_update_toxicity(message_ids=message_ids)
    message_ids = get_messageids_without_embedding()
    find_and_update_embeddings(message_ids=message_ids)
    return


if __name__ == "__main__":
    main()
