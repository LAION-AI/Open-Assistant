from uuid import UUID

from oasst_backend.models.message_tree_state import State as TreeState
from pydantic import BaseModel


class MessageTreeStateResponse(BaseModel):
    message_tree_id: UUID
    state: TreeState
    goal_tree_size: int
    max_depth: int
    max_children_count: int
    active: bool
    origin: str | None
