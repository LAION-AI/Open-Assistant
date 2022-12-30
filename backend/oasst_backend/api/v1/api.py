# -*- coding: utf-8 -*-
from fastapi import APIRouter
from oasst_backend.api.v1 import frontend_messages, frontend_users, messages, stats, tasks, text_labels, users

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(text_labels.router, prefix="/text_labels", tags=["text_labels"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(frontend_messages.router, prefix="/frontend_messages", tags=["frontend_messages"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(frontend_users.router, prefix="/frontend_users", tags=["frontend_users"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
