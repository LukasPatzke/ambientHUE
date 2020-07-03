from app import models
from app.database import SessionLocal, engine
from app.endpoints.curve import calc_curve_value
from app.endpoints.bridge import hue_api
import logging
import requests

log = logging.getLogger(__name__)


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
        log.info('disabled')
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
