from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.schedules import run
import logging

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=schemas.Status)
async def get_status(db: Session = Depends(get_db)) -> Any:
    return crud.status.get(db)


@router.put("/", response_model=schemas.Status)
async def update_status(
    status_in: schemas.StatusCreate,
    db: Session = Depends(get_db)
) -> Any:
    status = crud.status.get(db)
    status = crud.status.update(db, db_obj=status, obj_in=status_in)

    run(disable=True)

    return status
