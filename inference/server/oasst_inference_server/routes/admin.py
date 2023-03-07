import fastapi
import sqlmodel
from fastapi import Depends
from loguru import logger
from oasst_inference_server import deps, models
from oasst_inference_server.schemas import worker as worker_schema

router = fastapi.APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(deps.get_root_token)],
)


@router.put("/workers")
def create_worker(
    request: worker_schema.CreateWorkerRequest,
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Allows a client to register a worker."""
    logger.info(f"Creating worker {request.name=}")
    worker = models.DbWorker(name=request.name)
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


@router.get("/workers")
def list_workers(
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Lists all workers."""
    workers = session.exec(sqlmodel.select(models.DbWorker)).all()
    return list(workers)


@router.delete("/workers/{worker_id}")
def delete_worker(
    worker_id: str,
    session: sqlmodel.Session = Depends(deps.create_session),
):
    """Deletes a worker."""
    logger.info(f"Deleting worker {worker_id=}")
    worker = session.get(models.DbWorker, worker_id)
    session.delete(worker)
    session.commit()
    return fastapi.Response(status_code=200)
