from sqlmodel import create_engine
from app.config import settings

engine = create_engine(settings.DATABASE_URI)
