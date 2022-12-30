# -*- coding: utf-8 -*-
from fastapi import APIRouter
from oasst_backend.api.v1 import management, tasks, text_labels

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(text_labels.router, prefix="/text_labels", tags=["text_labels"])
api_router.include_router(management.router, prefix="/management", tags=["management"])
