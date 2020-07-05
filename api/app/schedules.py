from typing import Optional
from app import models, schemas
from app.database import SessionLocal, engine
from app.endpoints.bridge import hue_api
from app.interpolate import monospline
from sqlalchemy.orm import Session
import datetime as dt
import logging
import requests

log = logging.getLogger(__name__)


def calc_curve_value(
    db: Session,
    curve: schemas.Curve,
    x: Optional[int] = None
) -> int:
    """ Calculate the value from the points"""
    points = (db.query(models.Point)
                .with_parent(curve)
                .order_by(models.Point.x)
                .all())

    if x is None:
        now = dt.datetime.now()
        x = int((now - now.replace(hour=0,
                                   minute=0,
                                   second=0,
                                   microsecond=0)).total_seconds() / 60) - 4*60

    cs = monospline(
        xs=[point.x for point in points],
        ys=[point.y + curve.offset for point in points],
    )

    value = int(cs(x))
    return value


def run(disable=False):
    """ Calculate and execute the current state"""
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    status = db.query(models.Status).first()
    if status.status:
        lights = db.query(models.Light).all()

        for light in lights:
            body = {}

            brightness = calc_curve_value(db=db, curve=light.bri_curve)
            color_temp = calc_curve_value(db=db, curve=light.ct_curve)

            if light.ct_controlled:
                body['ct'] = color_temp

            light_brightness = (light.bri_max/254) * brightness
            if light_brightness > 0:
                if light.bri_controlled:
                    body['bri'] = int(light_brightness)
                if light.on_controlled:
                    if light_brightness > light.on_threshold:
                        body['on'] = True
                    else:
                        body['on'] = False
            elif light.on_controlled:
                body['on'] = False

            if body == {}:
                log.debug('skipping request, empty body')
            else:
                response = requests.put(
                    f'{hue_api()}/lights/{light.id}/state',
                    json=body
                )
                log.debug('response: %s', response.json())
    else:
        log.debug('disabled')
        if disable:
            lights = db.query(models.Light).filter_by(on_controlled=True).all()

            for light in lights:
                response = requests.put(
                    f'{hue_api()}/lights/{light.id}/state',
                    json={'on': False}
                )
                log.debug(response.json())
    db.close()


def reset_offsets():
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    curves = db.query(models.Curve).filter(models.Curve.offset != 0).all()

    for curve in curves:
        curve.offset = 0

    db.commit()
    db.close()

    log.info('Reset offset for %s curves', len(curves))
