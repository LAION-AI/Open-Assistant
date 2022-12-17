# -*- coding: utf-8 -*-
from fastapi import APIRouter
from ocgpt.api.v1 import tasks

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
