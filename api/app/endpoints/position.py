from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get('/', response_model=List[schemas.Position])
async def get_all_positions(
    db: Session = Depends(get_db)
) -> Any:
    return (db.query(models.Position)
              .order_by(models.Position.position)
              .all())


@router.put('/', response_model=List[schemas.Position])
async def move_position(
    move: schemas.PositionMove,
    db: Session = Depends(get_db)
) -> Any:
    positions = (db.query(models.Position)
                   .order_by(models.Position.position)
                   .all())

    position = positions.pop(move.move_from)
    positions.insert(move.move_to, position)

    for index, position in enumerate(positions):
        position.position = index

    db.commit()
    return (db.query(models.Position)
              .order_by(models.Position.position)
              .all())


@router.put('/{id}', response_model=List[schemas.Position])
async def update_position(
    id: int,
    position_in: schemas.PositionUpdate,
    db: Session = Depends(get_db)
) -> Any:
    position = db.query(models.Position).get(id)
    position.visible = position_in.visible
    db.commit()
    return (db.query(models.Position)
              .order_by(models.Position.position)
              .all())
