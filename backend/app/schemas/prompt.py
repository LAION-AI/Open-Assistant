# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    id: int
    labeler_id: int
    prompt: str
    response: Optional[str]
    lang: Optional[str]
    created_date: datetime


class PromptCreate(BaseModel):
    labeler_id: Optional[int] = None
    discord_username: Optional[str] = None
    prompt: str
    response: Optional[str] = None
    lang: Optional[str] = None
