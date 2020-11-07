from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Settings
from app.schemas import SettingsCreate, SettingsUpdate


class CRUDSettings(CRUDBase[Settings, SettingsCreate, SettingsUpdate]):
    def get(self, db: Session) -> Optional[Settings]:
        return db.query(self.model).first()


settings = CRUDSettings(Settings)
