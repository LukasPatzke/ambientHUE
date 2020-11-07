from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
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
) -> Any:
    return crud.bridge.create(db, bridge_in=bridge_in)


@router.get('/discover', response_model=List[schemas.BridgeDiscovery])
async def discover_bridges() -> Any:
    return requests.get('https://discovery.meethue.com/').json()


@router.get('/sync', response_model=schemas.BridgeSync)
async def sync_with_bridge(
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    return crud.bridge.sync(db, api)
