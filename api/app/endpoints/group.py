from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.schedules import run

router = APIRouter()


@router.get('/', response_model=List[schemas.Group])
async def get_all_groups(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Group).all()


@router.get('/{id}', response_model=schemas.Group)
async def get_group(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    group = db.query(models.Group).get(id)
    return group


@router.put('/{id}', response_model=schemas.Group)
async def update_group(
    id: int,
    light_in: schemas.LightUpdate,
    db: Session = Depends(get_db)
) -> Any:
    group = db.query(models.Group).get(id)

    for light in group.lights:
        for attr, value in light_in.dict().items():
            if value is not None:
                setattr(light, attr, value)

    db.commit()
    run(disable=True)
    return group
