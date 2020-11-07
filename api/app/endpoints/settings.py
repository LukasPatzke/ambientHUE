from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.api import ServerSession, get_api

router = APIRouter()


@router.get("/", response_model=schemas.Settings)
async def get_status(db: Session = Depends(get_db)) -> Any:
    return crud.settings.get(db)


@router.put("/", response_model=schemas.Settings)
async def update_status(
    settings_in: schemas.SettingsUpdate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api),
) -> Any:
    settings = crud.settings.get(db)
    settings = crud.settings.update(db, db_obj=settings, obj_in=settings_in)

    if settings_in.smart_off is False:
        lights = crud.light.get_multi(db)
        for light in lights:
            crud.light.reset_smart_off(db, api, light=light)

    return settings
