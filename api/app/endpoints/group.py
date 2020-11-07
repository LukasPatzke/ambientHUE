from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import get_api, ServerSession
from app import schemas, crud
from app.database import get_db
from app.schedules import run

router = APIRouter()


@router.get('/', response_model=List[schemas.Group])
async def get_all_groups(
    db: Session = Depends(get_db)
) -> Any:
    return crud.group.get_multi(db)


@router.get('/{id}', response_model=schemas.Group)
async def get_group(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return crud.group.get(db, id=id)


@router.put('/{id}', response_model=schemas.Group)
async def update_group(
    id: int,
    light_in: schemas.LightUpdate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    group = crud.group.get(db, id=id)

    for light in group.lights:
        crud.light.update(db, api,  light=light, light_in=light_in)
    
    if light_in.on is not None:
        crud.webhook.fire(group=group)

    run(disable=True, lights=group.lights, db=db, api=api)
    db.commit()
    return group
