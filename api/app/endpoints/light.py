from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import null
from app import models, schemas
from app.database import get_db
from app.schedules import run
from app.endpoints.webhook import fire_webhook

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
            if attr == 'on':
                fire_webhook(light=light)

                if not value:
                    light.smart_off_on = null()
                    light.smart_off_bri = null()
                    light.smart_off_ct = null()
    db.commit()
    run(disable=True, lights=[light])

    return light
