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
        try:
            response = super().request(method, url, *args, **kwargs)
        except requests.ConnectionError as e:
            raise HTTPException(
                status_code=500,
                detail=e
            )

        content = response.json()
        try:
            if content[0].get('error'):
                raise HTTPException(
                    status_code=500,
                    detail=content[0].get('error').get('description')
                )
        except KeyError:
            pass

        return content


hue_session = ServerSession()


# Dependecy
def get_api(
    db: Session = Depends(get_db)
):
    bridge = crud.bridge.get(db)

    if bridge is None:
        raise HTTPException(
            status_code=401,
            detail='Hue Bridge is not configured'
        )

    return api_from_bridge(bridge)


def api_from_bridge(bridge):
    url = f'http://{bridge.ipaddress}/api/{bridge.username}/'
    hue_session.prefix_url = url
    return hue_session
