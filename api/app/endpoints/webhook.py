from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
import logging
import requests

log = logging.getLogger(__name__)

router = APIRouter()


@router.get('/', response_model=List[schemas.Webhook])
async def get_all_webhooks(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Webhook).all()


@router.post('/', response_model=schemas.Webhook)
async def create_webhook(
    webhook_in: schemas.WebhookUpdate,
    db: Session = Depends(get_db)
) -> Any:
    webhook = models.Webhook(
        on=webhook_in.on,
        name=webhook_in.name,
        url=webhook_in.url,
        body=webhook_in.body,
        method=webhook_in.method
    )
    if webhook_in.lights:
        webhook.lights = db.query(models.Light).filter(
                models.Light.id.in_(tuple(webhook_in.lights))
            ).all()
    if webhook_in.groups:
        webhook.groups = db.query(models.Group).filter(
                models.Group.id.in_(tuple(webhook_in.groups))
            ).all()

    db.add(webhook)
    db.commit()
    return webhook


@router.get('/{id}', response_model=schemas.Webhook)
async def get_webhook(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Webhook).get(id)


@router.put('/{id}', response_model=schemas.Webhook)
async def update_webhook(
    id: int,
    webhook_in: schemas.WebhookUpdate,
    db: Session = Depends(get_db)
) -> Any:
    webhook = db.query(models.Webhook).get(id)
    for attr, value in webhook_in.dict().items():
        if attr == 'lights' and value is not None:
            webhook.lights = db.query(models.Light).filter(
                    models.Light.id.in_(tuple(value))
                ).all()
        elif attr == 'groups' and value is not None:
            webhook.groups = db.query(models.Group).filter(
                models.Group.id.in_(tuple(value))
            ).all()
        elif value is not None:
            setattr(webhook, attr, value)

    db.commit()
    return webhook


@router.delete('/{id}', response_model=schemas.Webhook)
async def delete_webhook(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    webhook = db.query(models.Webhook).get(id)

    db.delete(webhook)
    db.commit()
    return webhook


def fire_webhook(light: schemas.Light = None, group: schemas.Group = None):
    if light:
        for webhook in light.webhooks:
            execute_webhook(
                webhook=webhook,
                params={
                    'item': 'light',
                    'id': light.id,
                    'name': light.name,
                    'type': light.type,
                    'on': str(light.on).lower()
                }
            )

    elif group:
        for webhook in group.webhooks:
            execute_webhook(
                webhook=webhook,
                params={
                    'item': 'group',
                    'id': group.id,
                    'name': group.name,
                    'type': group.type,
                    'on': str(all(
                            [light.on for light in group.lights]
                        )).lower()
                }
            )


def execute_webhook(webhook: schemas.WebhookBase, params: dict):
    url = webhook.url.format(**params)
    log.debug('execute webhook url %s', url)

    try:
        if webhook.method == 'GET':
            return requests.get(url=url)
        elif webhook.method == 'POST':
            body = webhook.body.format(**params)
            return requests.post(url=url, json=body)
        else:
            return None
    except requests.exceptions.ConnectionError as e:
        log.warning('webhook failed %s', e)
