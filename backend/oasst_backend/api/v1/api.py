from fastapi import APIRouter
from oasst_backend.api.v1 import (
    admin,
    auth,
    frontend_messages,
    frontend_users,
    hugging_face,
    leaderboards,
    messages,
    stats,
    tasks,
    text_labels,
    trollboards,
    users,
)

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(text_labels.router, prefix="/text_labels", tags=["text_labels"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(frontend_messages.router, prefix="/frontend_messages", tags=["frontend_messages"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(frontend_users.router, prefix="/frontend_users", tags=["frontend_users"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(leaderboards.router, prefix="/leaderboards", tags=["leaderboards"])
api_router.include_router(trollboards.router, prefix="/trollboards", tags=["trollboards"])
api_router.include_router(hugging_face.router, prefix="/hf", tags=["hugging_face"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
