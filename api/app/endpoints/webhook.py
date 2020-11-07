from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()


@router.get('/', response_model=List[schemas.Webhook])
async def get_all_webhooks(
    db: Session = Depends(get_db)
) -> Any:
    return crud.webhook.get_multi(db)


@router.post('/', response_model=schemas.Webhook)
async def create_webhook(
    webhook_in: schemas.WebhookUpdate,
    db: Session = Depends(get_db)
) -> Any:
    return crud.webhook.create(db, obj_in=webhook_in)


@router.get('/{id}', response_model=schemas.Webhook)
async def get_webhook(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return crud.webhook.get(db, id=id)


@router.put('/{id}', response_model=schemas.Webhook)
async def update_webhook(
    id: int,
    webhook_in: schemas.WebhookUpdate,
    db: Session = Depends(get_db)
) -> Any:
    webhook = crud.webhook.get(db, id=id)
    return crud.webhook.update(db, db_obj=webhook, obj_in=webhook_in)


@router.delete('/{id}', response_model=schemas.Webhook)
async def delete_webhook(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return crud.webhook.remove(db, id=id)
