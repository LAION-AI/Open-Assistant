# -*- coding: utf-8 -*-
from app.config import settings
from sqlmodel import create_engine

engine = create_engine(settings.DATABASE_URI)
