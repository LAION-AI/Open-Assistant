from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Labeler(BaseModel):
    id: int
    discord_username: str
    display_name: str
    created_date: datetime
    is_enabled: str
    notes: Optional[str]


class LabelerCreate(BaseModel):
    discord_username: str
    display_name: Optional[str]
    is_enabled: Optional[bool] = True
    notes: Optional[str] = None


class LabelerUpdate(BaseModel):
    discord_username: Optional[str] = None
    display_name: Optional[str] = None
    enabled: Optional[bool] = None
    notes: Optional[str] = None
