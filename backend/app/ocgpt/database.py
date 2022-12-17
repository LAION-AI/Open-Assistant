# -*- coding: utf-8 -*-
from ocgpt.config import settings
from sqlmodel import create_engine

if settings.DATABASE_URI is None:
    raise ValueError("DATABASE_URI is not set")

engine = create_engine(settings.DATABASE_URI)
