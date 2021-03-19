from typing import Any, Union, Dict
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import requests
import logging

from app.crud.base import CRUDBase
from app.models import Webhook, Light, Group
from app.schemas import WebhookCreate, WebhookUpdate

log = logging.getLogger(__name__)


class CRUDWebhook(CRUDBase[Webhook, WebhookCreate, WebhookUpdate]):
    def create(self, db: Session, *, obj_in: WebhookCreate) -> Webhook:
        db_obj = self.model(
            on=obj_in.on,
            name=obj_in.name,
            url=obj_in.url,
            method=obj_in.method,
            body=obj_in.body
        )  # type: ignore

        if obj_in.lights:
            db_obj.lights = db.query(Light).filter(
                    Light.id.in_(tuple(obj_in.lights))
                ).all()
        if obj_in.groups:
            db_obj.groups = db.query(Group).filter(
                    Group.id.in_(tuple(obj_in.groups))
                ).all()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Webhook,
        obj_in: Union[WebhookUpdate, Dict[str, Any]]
    ) -> Webhook:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                value = update_data[field]
                if field == 'lights' and value is not None:
                    db_obj.lights = db.query(Light).filter(
                        Light.id.in_(tuple(value))
                    ).all()
                elif field == 'groups' and value is not None:
                    db_obj.groups = db.query(Group).filter(
                        Group.id.in_(tuple(value))
                    ).all()
                else:
                    setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def fire(
        self,
        light: Light = None,
        group: Group = None
    ):
        """Fire all webhooks attached to light and group"""
        if light:
            for webhook in light.webhooks:
                self.execute(
                    webhook=webhook,
                    params={
                        'item': 'light',
                        'id': light.id,
                        'name': light.name,
                        'type': light.type,
                        'on': str(light.on).lower()
                    }
                )

        if group:
            for webhook in group.webhooks:
                self.execute(
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

    def execute(self, webhook: Webhook, params: dict):
        """Execute a specific webhook"""
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


webhook = CRUDWebhook(Webhook)
