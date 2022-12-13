from fastapi import APIRouter

from app.api.v1 import labelers, prompts

api_router = APIRouter()
api_router.include_router(labelers.router, prefix="/labelers", tags=["labelers"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
