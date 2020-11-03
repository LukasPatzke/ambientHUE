from typing import Optional
from sqlalchemy.orm import Session
from app.api import ServerSession
import logging
import requests
import time
from socket import gethostname
from fastapi import HTTPException

from app.crud.base import CRUDBase
from app.models import Bridge, Position
from app.schemas import BridgeCreate, BridgeUpdate, BridgeSync

from .crud_group import group as crud_group
from .crud_light import light as crud_light

log = logging.getLogger(__name__)


class CRUDBridge(CRUDBase[Bridge, BridgeCreate, BridgeUpdate]):
    def get(self, db: Session) -> Optional[Bridge]:
        return db.query(self.model).first()

    def create(
        self,
        db: Session,
        api: ServerSession,
        *,
        bridge_in: BridgeCreate
    ) -> BridgeSync:
        counter = 0
        while counter < 100:
            response = requests.post(
                f'http://{bridge_in.ipaddress}/api',
                json={'devicetype': f'hue_dimmer#{gethostname()}'}
            ).json()
            log.info(response)
            if response[0].get('success'):
                break
            time.sleep(1)
            counter += 1

        if not response[0].get('success'):
            raise HTTPException(
                status_code=500,
                detail=response
            )

        username = response[0]['success']['username']
        info = requests.get(
            f'http://{bridge_in.ipaddress}/api/{username}/config'
        ).json()
        log.info('Bridge registered %s', info)

        bridge = self.get(db)
        new_bridge = Bridge(
            id=info.get('bridgeid'),
            name=info.get('name'),
            ipaddress=info.get('ipaddress'),
            username=username
        )
        db.add(new_bridge)
        if bridge:
            db.delete(bridge)
        db.commit()

        return self.sync(db, api)

    def sync(self, db: Session, api: ServerSession):

        hue_lights = api.get('/lights').json()
        hue_groups = api.get('/groups').json()

        lights = {light.id: light for light in crud_light.get_multi(db)}
        groups = {groups.id: groups for groups in crud_group.get_multi(db)}

        for light_id, hue_light in hue_lights.items():
            light = lights.get(int(light_id))
            if not light:
                light = crud_light.create(db, obj_in={
                    'id': int(light_id),
                    'position': Position(),
                    'name': hue_light.get('name'),
                    'type': hue_light.get('type'),
                    'modelid': hue_light.get('modelid'),
                    'manufacturername': hue_light.get('manufacturername'),
                    'productname': hue_light.get('productname')
                })
            else:
                light = crud_light.update(db, api, light=light, light_in={
                    'name': hue_light.get('name'),
                    'type': hue_light.get('type'),
                    'modelid': hue_light.get('modelid'),
                    'manufacturername': hue_light.get('manufacturername'),
                    'productname': hue_light.get('productname')
                })

        for light_id, light in lights.items():
            if str(light_id) not in hue_lights:
                crud_light.remove(db, id=light.id)

        for group_id, hue_group in hue_groups.items():
            group = groups.get(int(group_id))
            if not group:
                group = crud_group.create(db, obj_in={
                    'id': int(group_id),
                    'position': Position(),
                    'name': hue_group.get('name'),
                    'type': hue_group.get('type'),
                    'lights': (
                        [crud_light.get(db, id=int(id))
                            for id in hue_group['lights']]
                    )
                })
            else:
                group = crud_group.update(db, db_obj=group, obj_in={
                    'name': hue_group.get('name'),
                    'type': hue_group.get('type'),
                    'lights': (
                        [crud_light.get(db, id=int(id))
                            for id in hue_group['lights']]
                    )
                })

        for group_id, group in groups.items():
            if str(group_id) not in hue_groups:
                crud_group.remove(db, id=group.id)

        return {
            'lights': crud_light.count(db),
            'groups': crud_group.count(db)
        }


bridge = CRUDBridge(Bridge)
