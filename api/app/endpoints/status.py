from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.Status)
async def get_status(db: Session = Depends(get_db)) -> Any:
    return db.query(models.Status).first()


@router.put("/", response_model=schemas.Status)
async def update_status(
    status_in: schemas.StatusCreate,
    db: Session = Depends(get_db)
) -> Any:
    status = db.query(models.Status).first()
    status.status = status_in.status
    db.commit()
    return status
