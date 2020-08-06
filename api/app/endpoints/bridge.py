from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db, SessionLocal, engine
import requests
import socket
import time
import logging

log = logging.getLogger(__name__)

router = APIRouter()


@router.get('/', response_model=schemas.Bridge)
async def get_bridge(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Bridge).first()


@router.post('/', response_model=schemas.BridgeSync)
async def create_bridge(
    bridge_in: schemas.BridgeCreate,
    db: Session = Depends(get_db)
) -> Any:

    counter = 0
    while counter < 100:
        response = requests.post(
            f'http://{bridge_in.ipaddress}/api',
            json={'devicetype': f'hue_dimmer#{socket.gethostname()}'}
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
    log.info(info)
    bridge = db.query(models.Bridge).first()
    new_bridge = models.Bridge(
        id=info.get('bridgeid'),
        name=info.get('name'),
        ipaddress=info.get('ipaddress'),
        username=username
    )
    db.add(new_bridge)
    if bridge:
        db.delete(bridge)
    db.commit()

    return sync()


@router.get('/discover', response_model=List[schemas.BridgeDiscovery])
async def discover_bridges() -> Any:
    return requests.get('https://discovery.meethue.com/').json()


@router.get('/sync', response_model=schemas.BridgeSync)
async def sync_with_bridge() -> Any:
    return sync()


def sync() -> schemas.BridgeSync:
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    hue_lights = requests.get(f'{hue_api()}/lights').json()
    hue_groups = requests.get(f'{hue_api()}/groups').json()

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
        if light_id not in hue_lights:
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
        if group_id not in hue_groups:
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
