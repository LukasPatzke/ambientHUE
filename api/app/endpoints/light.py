from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.api import get_api, ServerSession
from app.schedules import run

router = APIRouter()


@router.get('/', response_model=List[schemas.Light])
async def get_all_lights(
    db: Session = Depends(get_db)
) -> Any:
    return crud.light.get_multi(db)


@router.get('/{id}', response_model=schemas.Light)
async def get_light(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return crud.light.get(db, id=id)


@router.put('/{id}', response_model=schemas.Light)
async def update_light(
    id: int,
    light_in: schemas.LightUpdate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api),
) -> Any:
    light = crud.light.get(db, id=id)
    light = crud.light.update(db, api, light=light, light_in=light_in)
    run(disable=True, lights=[light], db=db, api=api)
    db.add(light)
    db.commit()
    db.refresh(light)
    return light
