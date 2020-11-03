from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import get_db, SessionLocal, engine
from app.api import get_api, ServerSession
import requests
import logging

log = logging.getLogger(__name__)

router = APIRouter()


@router.get('/', response_model=schemas.Bridge)
async def get_bridge(
    db: Session = Depends(get_db)
) -> Any:
    return crud.bridge.get(db)


@router.post('/', response_model=schemas.BridgeSync)
async def create_bridge(
    bridge_in: schemas.BridgeCreate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:

    return crud.bridge.create(db, api, bridge_in=bridge_in)


@router.get('/discover', response_model=List[schemas.BridgeDiscovery])
async def discover_bridges() -> Any:
    return requests.get('https://discovery.meethue.com/').json()


@router.get('/sync', response_model=schemas.BridgeSync)
async def sync_with_bridge(
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    return crud.bridge.sync(db, api)


def sync() -> schemas.BridgeSync:
    db = SessionLocal()
    api = hue_api()

    hue_lights = requests.get(f'{api}/lights').json()
    hue_groups = requests.get(f'{api}/groups').json()

    lights = {light.id: light for light in db.query(models.Light).all()}
    groups = {groups.id: groups for groups in db.query(models.Group).all()}

    for light_id, hue_light in hue_lights.items():
        light = lights.get(int(light_id))
        if not light:
            light = models.Light(
                id=int(light_id),
                position=models.Position()
            )
            db.add(light)

        light.name = hue_light['name']
        light.type = hue_light['type']
        light.modelid = hue_light['modelid']
        light.manufacturername = hue_light['manufacturername']
        light.productname = hue_light['productname']

    for light_id, light in lights.items():
        if str(light_id) not in hue_lights:
            db.delete(light)
    db.commit()

    for group_id, hue_group in hue_groups.items():
        group = groups.get(int(group_id))
        if not group:
            group = models.Group(id=int(group_id), position=models.Position())
            db.add(group)
        group.name = hue_group['name']
        group.type = hue_group['type']
        group.lights = (
            [db.query(models.Light).get(int(li)) for li in hue_group['lights']]
        )

    for group_id, group in groups.items():
        if str(group_id) not in hue_groups:
            db.delete(group)
    db.commit()
    db.close()

    return {
        'lights': db.query(models.Light).count(),
        'groups': db.query(models.Group).count()
    }


def hue_api() -> str:
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    bridge = db.query(models.Bridge).first()

    db.close()
    if bridge is None:
        log.warning('Hue Bridge is not configured')
        return None
    else:
        return f'http://{bridge.ipaddress}/api/{bridge.username}'
