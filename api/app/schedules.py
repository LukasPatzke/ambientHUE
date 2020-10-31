from typing import Optional
from functools import lru_cache
from app import models, schemas
from app.database import SessionLocal, engine
from app.endpoints.bridge import hue_api
from app.interpolate import monospline
from sqlalchemy.orm import Session
from sqlalchemy.sql import null
import datetime as dt
import logging
import requests

log = logging.getLogger(__name__)


@lru_cache()
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


def get_smart_off(light, prev_light_state):

    smart_off_on = (
        (light.smart_off_on is not None) and
        (light.smart_off_on != prev_light_state.get('on'))
    )
    smart_off_bri = (
        (light.smart_off_bri is not None) and
        (light.smart_off_bri != prev_light_state.get('bri'))
    )
    smart_off_ct = (
        (light.smart_off_ct is not None) and
        (light.smart_off_ct != prev_light_state.get('ct'))
    )

    return smart_off_on or smart_off_bri or smart_off_ct


def get_request_body(db, light):
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
            if light.on is False:
                body['on'] = False
            elif light_brightness > light.on_threshold:
                body['on'] = True
            else:
                body['on'] = False
    elif light.on_controlled:
        body['on'] = False

    return body


def run(disable=False, lights=None):
    """ Calculate and execute the current state"""
    db = SessionLocal()

    status = db.query(models.Status).first()
    api = hue_api()
    if status.status:
        settings = db.query(models.Settings).first()

        hue_prev = requests.get(f'{api}/lights').json()
        if not lights:
            lights = db.query(models.Light).all()

        bri_default = (db.query(models.Curve).filter_by(default=True)
                                             .filter_by(kind='bri').first())
        ct_default = (db.query(models.Curve).filter_by(default=True)
                                            .filter_by(kind='ct').first())

        for light in lights:
            prev_light_state = hue_prev.get(str(light.id)).get('state')

            if settings.smart_off:
                smart_off = get_smart_off(light, prev_light_state)

                if smart_off:
                    log.debug(
                        'skipping request, Smart Off for light %s',
                        light.id
                    )
                    continue

            body = {}

            bri_curve = light.bri_curve or bri_default
            ct_curve = light.ct_curve or ct_default

            brightness = calc_curve_value(db=db, curve=bri_curve)
            color_temp = calc_curve_value(db=db, curve=ct_curve)

            if light.ct_controlled:
                body['ct'] = color_temp

            light_brightness = (light.bri_max/254) * brightness
            if light_brightness > 0:
                if light.bri_controlled:
                    body['bri'] = int(light_brightness)
                if light.on_controlled:
                    if light.on is False:
                        body['on'] = False
                    elif light_brightness > light.on_threshold:
                        body['on'] = True
                    else:
                        body['on'] = False
            elif light.on_controlled:
                body['on'] = False

            if body == {}:
                log.debug('skipping request, empty body')
            if not (body.get('on') or (prev_light_state.get('on'))):
                log.debug('skipping request, light %s is off', light.id)
            else:
                response = requests.put(
                    f'{api}/lights/{light.id}/state',
                    json=body
                )
                log.debug('response: %s', response.json())

        if settings.smart_off:
            for light in lights:
                hue_next = requests.get(
                    f'{api}/lights/{light.id}'
                ).json()
                hue_next_state = hue_next.get('state')
                light.smart_off_on = hue_next_state.get('on', null())
                light.smart_off_bri = hue_next_state.get('bri', null())
                light.smart_off_ct = hue_next_state.get('ct', null())

                db.commit()

    else:
        log.debug('disabled')
        if disable:
            lights = db.query(models.Light).filter_by(on_controlled=True).all()

            for light in lights:
                response = requests.put(
                    f'{api}/lights/{light.id}/state',
                    json={'on': False}
                )
                log.debug(response.json())
    db.close()
    calc_curve_value.cache_clear()


def reset_offsets():
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    curves = db.query(models.Curve).filter(models.Curve.offset != 0).all()
    for curve in curves:
        curve.offset = 0

    lights = db.query(models.Light).all()
    for light in lights:
        light.smart_off_on = null()
        light.smart_off_bri = null()
        light.smart_off_ct = null()

    db.commit()
    db.close()

    log.info('Reset offset for %s curves', len(curves))


if __name__ == '__main__':
    run()
