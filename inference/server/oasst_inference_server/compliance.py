import datetime
from typing import cast

import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import database, deps, models, worker_utils
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from sqlalchemy.sql.functions import random as sql_random
from sqlmodel import not_, or_


async def find_compliance_work_request_message(
    session: database.AsyncSession, worker_config: inference.WorkerConfig, worker_id: str
) -> models.DbMessage | None:
    compat_hash = worker_config.compat_hash
    query = (
        sqlmodel.select(models.DbMessage)
        .where(
            models.DbMessage.role == "assistant",
            models.DbMessage.state == inference.MessageState.complete,
            models.DbMessage.worker_compat_hash == compat_hash,
            models.DbMessage.worker_id != worker_id,
        )
        .order_by(sql_random())
    )
    message = (await session.exec(statement=query)).first()
    return message


async def should_do_compliance_check(session: database.AsyncSession, worker_id: str) -> bool:
    worker = await worker_utils.get_worker(worker_id=worker_id, session=session)
    if worker.trusted:
        return False
    if worker.in_compliance_check:
        return False
    if worker.next_compliance_check is None:
        return True
    if worker.next_compliance_check < datetime.datetime.utcnow():
        return True
    return False


async def run_compliance_check(websocket: fastapi.WebSocket, worker_id: str, worker_config: inference.WorkerConfig):
    async with deps.manual_create_session() as session:
        try:
            worker = await worker_utils.get_worker(worker_id=worker_id, session=session)
            if worker.in_compliance_check:
                logger.info(f"Worker {worker.id} is already in compliance check")
                return
            worker.in_compliance_check_since = datetime.datetime.utcnow()
        finally:
            await session.commit()

    logger.info(f"Running compliance check for worker {worker_id}")

    async with deps.manual_create_session(autoflush=False) as session:
        compliance_check = models.DbWorkerComplianceCheck(worker_id=worker_id)

        try:
            message = await find_compliance_work_request_message(
                session=session, worker_config=worker_config, worker_id=worker_id
            )
            if message is None:
                logger.warning(
                    f"Could not find message for compliance check for worker {worker_id} with config {worker_config}"
                )
                return

            compliance_check.compare_worker_id = message.worker_id
            compliance_work_request = await worker_utils.build_work_request(session=session, message_id=message.id)

            logger.info(f"Found work request for compliance check for worker {worker_id}: {compliance_work_request}")
            await worker_utils.send_worker_request(websocket=websocket, request=compliance_work_request)
            response = None
            while True:
                response = await worker_utils.receive_worker_response(websocket=websocket)
                if response.response_type == "error":
                    compliance_check.responded = True
                    compliance_check.error = response.error
                    logger.warning(f"Worker {worker_id} errored during compliance check: {response.error}")
                    return
                if response.response_type == "generated_text":
                    break
            if response is None:
                logger.warning(f"Worker {worker_id} did not respond to compliance check")
                return
            compliance_check.responded = True
            response = cast(inference.GeneratedTextResponse, response)
            passes = response.text == message.content
            compliance_check.passed = passes
            logger.info(f"Worker {worker_id} passed compliance check: {passes}")

        finally:
            compliance_check.end_time = datetime.datetime.utcnow()
            session.add(instance=compliance_check)
            worker = await worker_utils.get_worker(worker_id=worker_id, session=session)
            worker.next_compliance_check = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=settings.compliance_check_interval
            )
            worker.in_compliance_check_since = None
            logger.info(f"set next compliance check for worker {worker_id} to {worker.next_compliance_check}")
            await session.commit()
            await session.flush()


async def maybe_do_compliance_check(websocket, worker_id, worker_config, worker_session_id):
    async with deps.manual_create_session() as session:
        should_check = await should_do_compliance_check(session=session, worker_id=worker_id)
    if should_check:
        logger.info(f"Worker {worker_id} needs compliance check")
        try:
            await worker_utils.update_worker_session_status(
                worker_session_id, worker_utils.WorkerSessionStatus.compliance_check
            )
            await run_compliance_check(websocket=websocket, worker_id=worker_id, worker_config=worker_config)
        finally:
            await worker_utils.update_worker_session_status(worker_session_id, worker_utils.WorkerSessionStatus.waiting)


async def compute_worker_compliance_score(worker_id: str) -> float:
    """
    Compute a float between 0 and 1 (inclusive) representing the compliance score of the worker.
    Workers are rewarded for passing compliance checks, and penalised for failing to respond to a check, erroring during a check, or failing a check.
    In-progress checks are ignored.
    """
    async with deps.manual_create_session() as session:
        query = sqlmodel.select(models.DbWorkerComplianceCheck).where(
            or_(
                models.DbWorkerComplianceCheck.worker_id == worker_id,
                models.DbWorkerComplianceCheck.compare_worker_id == worker_id,
            ),
            not_(clause=models.DbWorkerComplianceCheck.end_time.is_(None)),
        )
        worker_checks: list[models.DbWorkerComplianceCheck] = (await session.exec(statement=query)).all()

        # Rudimentary scoring algorithm, we may want to add weightings or other factors
        total_count = len(worker_checks)

        checked = [c for c in worker_checks if c.worker_id == worker_id]
        compared = [c for c in worker_checks if c.compare_worker_id == worker_id]

        pass_count = sum(1 for _ in filter(lambda c: c.passed, checked))
        error_count = sum(1 for _ in filter(lambda c: c.error is not None, checked))
        no_response_count = sum(1 for _ in filter(lambda c: not c.responded, checked))

        compare_fail_count = sum(1 for _ in filter(lambda c: not c.passed, compared))
        fail_count = len(checked) - pass_count - error_count - no_response_count

        return (fail_count + compare_fail_count) / total_count
