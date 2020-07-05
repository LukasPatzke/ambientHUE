from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.schedules import run

router = APIRouter()


@router.get('/', response_model=List[schemas.Light])
async def get_all_lights(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Light).all()


@router.get('/{id}', response_model=schemas.Light)
async def get_light(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Light).get(id)


@router.put('/{id}', response_model=schemas.Light)
async def update_light(
    id: int,
    light_in: schemas.LightUpdate,
    db: Session = Depends(get_db)
) -> Any:
    light = db.query(models.Light).get(id)

    for attr, value in light_in.dict().items():
        if value is not None:
            setattr(light, attr, value)
    db.commit()
    run(disable=True)

    return light
