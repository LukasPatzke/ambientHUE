from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Status
from app.schemas import StatusCreate


class CRUDStatus(CRUDBase[Status, StatusCreate, StatusCreate]):
    def get(self, db: Session) -> Optional[Status]:
        return db.query(self.model).first()


status = CRUDStatus(Status)
