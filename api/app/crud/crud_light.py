from typing import Any, Union, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import null
from app.api import ServerSession
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models import Light
from app.schemas import LightCreate, LightUpdate
from .crud_webhook import webhook


class CRUDLight(CRUDBase[Light, LightCreate, LightUpdate]):
    def get_multi_controlled(
        self,
        db: Session
    ) -> List[Light]:
        return db.query(Light).filter_by(on_controlled=True).all()

    def update(
        self,
        db: Session,
        api: ServerSession,
        *,
        light: Light,
        light_in: Union[LightUpdate, Dict[str, Any]]
    ) -> Light:
        obj_data = jsonable_encoder(light)
        if isinstance(light_in, dict):
            update_data = light_in
        else:
            update_data = light_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(light, field, update_data[field])
                if field == 'on':
                    webhook.fire(light=light)

        if update_data.get('on') is False:
            light = self.reset_smart_off(db, api, light=light)

        return light

    def reset_smart_off(
        self,
        db: Session,
        api: ServerSession,
        *,
        light: Light
    ) -> Light:
        hue = api.get(f'/lights/{light.id}').json()
        hue_state = hue.get('state')

        light.smart_off_on = hue_state.get('on', null())
        light.smart_off_bri = hue_state.get('bri', null())
        light.smart_off_ct = hue_state.get('ct', null())

        return light

    def count(self, db: Session) -> int:
        return db.query(Light).count()


light = CRUDLight(Light)
