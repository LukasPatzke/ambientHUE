from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
import requests
from urllib.parse import urljoin
from app.database import get_db
from app import crud


class ServerSession(requests.Session):
    """ A requests session with support for a url prefix."""
    def __init__(self, prefix_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url.lstrip('/'))
        return super().request(method, url, *args, **kwargs)


# Dependecy
def get_api(
    db: Session = Depends(get_db)
):
    try:
        bridge = crud.bridge.get(db)

        if bridge is None:
            raise HTTPException(
                status_code=404,
                detail='Hue Bridge is not configured'
            )

        url = f'http://{bridge.ipaddress}/api/{bridge.username}/'

        session = ServerSession(prefix_url=url)

        yield session
    finally:
        session.close()
