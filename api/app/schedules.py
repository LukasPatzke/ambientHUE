from app import models, crud
from app.database import SessionLocal
from app.api import get_api
from sqlalchemy.orm import Session
import logging


log = logging.getLogger(__name__)


def calc_brightness(db: Session, light: models.Light):
    """ Calculate the current brightness for a light. """
    curve = light.bri_curve
    if not curve:
        curve = crud.curve.get_default_by_kind(db, kind='bri')
    curve_value = crud.curve.calc_value(db=db, curve=curve)
    return int((light.bri_max/254) * curve_value)


def calc_color_temp(db: Session, light: models.Light):
    """ Calculate the current color temperature for a light. """
    curve = light.ct_curve
    if not curve:
        curve = crud.curve.get_default_by_kind(db, kind='ct')
    return crud.curve.calc_value(db=db, curve=curve)


def get_smart_off(light, prev_light_state):
    """ Calculate the smart of state. """
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


def get_request_body(db, light, prev_light_state):
    """ Build the request body for the hue api."""
    body = {}

    brightness = calc_brightness(db=db, light=light)
    color_temp = calc_color_temp(db=db, light=light)

    if light.ct_controlled:
        body['ct'] = color_temp
    if light.bri_controlled:
        body['bri'] = brightness
    if light.on_controlled:
        if light.on is False:
            body['on'] = False
        elif brightness > light.on_threshold:
            body['on'] = True
        else:
            body['on'] = False

    if body.get('on') is False:
        return {'on': False}

    # Signify recommends to not resent the 'on' value
    if body.get('on') == prev_light_state.get('on'):
        del body['on']
    log.debug('body: %s', body)
    return body


def run(disable=False, lights=None, db=None, api=None):
    """ Calculate and execute the current state"""

    status = crud.status.get(db)
    if status.status:
        settings = crud.settings.get(db)

        hue_prev = api.get('/lights').json()

        if not lights:
            lights = crud.light.get_multi(db)

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

            body = get_request_body(
                db=db,
                light=light,
                prev_light_state=prev_light_state
            )

            if body == {}:
                log.debug(
                    'skipping request, empty body for light %s.',
                    light.id
                )
            else:
                response = api.put(
                    f'/lights/{light.id}/state',
                    json=body
                )
                log.debug('response: %s', response.json())
                if settings.smart_off:
                    crud.light.reset_smart_off(db, api, light=light)
                    # db.commit()

    else:
        log.debug('disabled')
        if disable:
            if not lights:
                lights = crud.light.get_multi_controlled(db)

            for light in lights:
                response = api.put(
                    f'/lights/{light.id}/state',
                    json={'on': False}
                )
                log.debug(response.json())
    crud.curve.calc_value.cache_clear()


def scheduled_run():
    db = SessionLocal()
    api = next(get_api(db))
    run(db=db, api=api)


def reset_offsets():
    db = SessionLocal()

    curves = crud.curve.get_multi(db)
    for curve in curves:
        crud.curve.update(db, db_obj=curve, obj_in={
            'offset': 0
        })
    log.info('Reset offset for %s curves', len(curves))

    reset_smart_off()


def reset_smart_off():
    db = SessionLocal()
    api = next(get_api(db))
    lights = crud.light.get_multi(db)
    for light in lights:
        crud.light.reset_smart_off(db, api, light=light)
    db.commit()
    log.info('Reset smart off for %s lights', len(lights))
    db.close()


if __name__ == '__main__':
    run()
