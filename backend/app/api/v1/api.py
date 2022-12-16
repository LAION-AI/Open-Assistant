# -*- coding: utf-8 -*-
from app.api.v1 import tasks
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
