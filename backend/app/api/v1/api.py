# -*- coding: utf-8 -*-
from app.api.v1 import tasks, tasks2
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

api_router.include_router(tasks2.router, prefix="/task2", tags=["task2"])  # temporary
