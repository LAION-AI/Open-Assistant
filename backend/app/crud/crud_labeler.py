from typing import Optional

from app.crud.base import CRUDBase
from app.models.labeler import Labeler
from app.schemas.labeler import LabelerCreate, LabelerUpdate
from sqlmodel import Session


class CRUDLabeler(CRUDBase[Labeler, LabelerCreate, LabelerUpdate]):
    def get_by_discord_username(self, db: Session, discord_username: str) -> Optional[Labeler]:
        return db.query(Labeler).filter(Labeler.discord_username == discord_username).first()


labeler = CRUDLabeler(Labeler)
