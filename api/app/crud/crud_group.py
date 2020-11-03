from sqlalchemy.orm import Session

from .base import CRUDBase
from app.models import Group
from app.schemas import GroupCreate, GroupUpdate


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    def count(self, db: Session) -> int:
        return db.query(Group).count()


group = CRUDGroup(Group)
