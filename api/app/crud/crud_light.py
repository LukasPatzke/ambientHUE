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

        if update_data.get('on') is not None:
            light = self.reset_smart_off(db, api, light=light)
        return light

    def get_smart_off(
        self,
        light: Light,
        prev_light_state
    ):
        """ Calculate the smart of state. """
        if light.on_controlled:
            smart_off_on = (
                (light.smart_off_on is not None) and
                (light.smart_off_on != prev_light_state.get('on'))
            )
        else:
            smart_off_on = False
        if light.bri_controlled:
            smart_off_bri = (
                (light.smart_off_bri is not None) and
                (light.smart_off_bri != prev_light_state.get('bri'))
            )
        else:
            smart_off_bri = False
        if light.ct_controlled:
            smart_off_ct = (
                (light.smart_off_ct is not None) and
                (light.smart_off_ct != prev_light_state.get('ct'))
            )
        else:
            smart_off_ct = False

        active = smart_off_on or smart_off_bri or smart_off_ct
        light.smart_off_active = active
        return light

    def reset_smart_off(
        self,
        db: Session,
        api: ServerSession,
        *,
        light: Light
    ) -> Light:
        hue = api.get(f'/lights/{light.id}')
        hue_state = hue.get('state')

        light.smart_off_on = hue_state.get('on', null())
        light.smart_off_bri = hue_state.get('bri', null())
        light.smart_off_ct = hue_state.get('ct', null())
        light.smart_off_active = False

        return light

    def count(self, db: Session) -> int:
        return db.query(Light).count()


light = CRUDLight(Light)
