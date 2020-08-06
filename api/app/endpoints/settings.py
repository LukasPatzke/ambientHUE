from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import null
from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.Settings)
async def get_status(db: Session = Depends(get_db)) -> Any:
    return db.query(models.Settings).first()


@router.put("/", response_model=schemas.Settings)
async def update_status(
    settings_in: schemas.SettingsUpdate,
    db: Session = Depends(get_db)
) -> Any:
    settings = db.query(models.Settings).first()
    for attr, value in settings_in.dict().items():
        if value is not None:
            setattr(settings, attr, value)

    if settings_in.smart_off is False:
        lights = db.query(models.Light).all()
        for light in lights:
            light.smart_off_on = null()
            light.smart_off_bri = null()
            light.smart_off_ct = null()

    db.commit()
    return settings
