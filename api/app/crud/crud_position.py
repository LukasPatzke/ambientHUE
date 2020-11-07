from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Position
from app.schemas import PositionMove, PositionUpdate, PositionCreate


class CRUDPosition(CRUDBase[Position, PositionCreate, PositionUpdate]):
    def get_multi(
        self,
        db: Session,
    ) -> List[Position]:
        return (db.query(Position)
                  .order_by(Position.position)
                  .all())

    def move(
        self,
        db: Session,
        *,
        move: PositionMove
    ) -> List[Position]:
        positions = self.get_multi(db)

        position = positions.pop(move.move_from)
        positions.insert(move.move_to, position)

        for index, position in enumerate(positions):
            position.position = index

        db.commit()
        return positions


position = CRUDPosition(Position)
