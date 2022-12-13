# -*- coding: utf-8 -*-
from typing import Optional

from sqlmodel import Field, SQLModel


class ServiceClient(SQLModel, table=True):
    __tablename__ = "service_client"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    api_key: str
    service_admin_email: Optional[str] = None
    api_key: str
    can_append: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_read: bool = True
