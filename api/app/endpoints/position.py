from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()


@router.get('/', response_model=List[schemas.Position])
async def get_all_positions(
    db: Session = Depends(get_db)
) -> Any:
    return crud.position.get_multi(db)


@router.put('/', response_model=List[schemas.Position])
async def move_position(
    move: schemas.PositionMove,
    db: Session = Depends(get_db)
) -> Any:
    return crud.position.move(db, move=move)


@router.put('/{id}', response_model=List[schemas.Position])
async def update_position(
    id: int,
    position_in: schemas.PositionUpdate,
    db: Session = Depends(get_db)
) -> Any:
    position = crud.position.get(db, id=id)
    position = crud.position.update(db, db_obj=position, obj_in=position_in)
    return crud.position.get_multi(db)
