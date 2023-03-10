import fastapi
import sqlmodel
from fastapi import Depends, HTTPException
from loguru import logger
from oasst_inference_server import database, deps, models
from oasst_inference_server.schemas import worker as worker_schema
from oasst_inference_server.settings import settings

router = fastapi.APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_bearer_token(authorization_header: str) -> str:
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must start with 'Bearer '")
    return authorization_header[len("Bearer ") :]


def get_root_token(token: str = Depends(get_bearer_token)) -> str:
    root_token = settings.root_token
    if token == root_token:
        return token
    raise HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@router.put("/workers")
async def create_worker(
    request: worker_schema.CreateWorkerRequest,
    root_token: str = Depends(get_root_token),
    session: database.AsyncSession = Depends(deps.create_session),
) -> worker_schema.WorkerRead:
    """Allows a client to register a worker."""
    logger.info(f"Creating worker {request.name}")
    worker = models.DbWorker(name=request.name, trusted=request.trusted)
    session.add(worker)
    await session.commit()
    await session.refresh(worker)
    return worker_schema.WorkerRead.from_orm(worker)


@router.get("/workers")
async def list_workers(
    root_token: str = Depends(get_root_token),
    session: database.AsyncSession = Depends(deps.create_session),
) -> list[worker_schema.WorkerRead]:
    """Lists all workers."""
    workers = (await session.exec(sqlmodel.select(models.DbWorker))).all()
    return [worker_schema.WorkerRead.from_orm(worker) for worker in workers]


@router.delete("/workers/{worker_id}")
async def delete_worker(
    worker_id: str,
    root_token: str = Depends(get_root_token),
    session: database.AsyncSession = Depends(deps.create_session),
):
    """Deletes a worker."""
    logger.info(f"Deleting worker {worker_id}")
    worker = await session.get(models.DbWorker, worker_id)
    session.delete(worker)
    await session.commit()
    return fastapi.Response(status_code=200)
