from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get('/', response_model=List[schemas.Header])
async def get_all_header(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Header).all()


@router.post('/', response_model=schemas.Header)
async def create_header(
    db: Session = Depends(get_db)
) -> Any:
    header = models.Header()
    db.add(header)
    db.commit()
    return header


@router.get('/{id}', response_model=schemas.Header)
async def get_header(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Header).get(id)


@router.put('/{id}', response_model=schemas.Header)
async def update_header(
    id: int,
    header_in: schemas.HeaderUpdate,
    db: Session = Depends(get_db)
) -> Any:
    header = db.query(models.Header).get(id)
    for attr, value in header_in.dict().items():
        if value is not None:
            setattr(header, attr, value)

    db.commit()
    return header


@router.delete('/{id}', response_model=schemas.Header)
async def delete_header(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    header = db.query(models.Header).get(id)

    db.delete(header)
    db.commit()
    return header
