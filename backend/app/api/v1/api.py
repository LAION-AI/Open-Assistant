# -*- coding: utf-8 -*-
from app.api.v1 import labelers, prompts, tasks
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(labelers.router, prefix="/labelers", tags=["labelers"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
