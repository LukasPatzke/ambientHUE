from app import models, crud
from app.database import SessionLocal


def init():
    db = SessionLocal()

    status = crud.status.get(db)
    if not status:
        crud.status.create(db, obj_in={
            'id': 0,
            'status': False
        })

    settings = crud.settings.get(db)
    if not settings:
        crud.settings.create(db, obj_in={
            'id': 0,
            'smart_off': True
        })

    bri_curve = crud.curve.get_default_by_kind(db, kind='bri')
    if not bri_curve:
        bri_curve = models.Curve(name='Default', kind='bri', default=True)
        models.Point(x=0, y=245, first=True, curve=bri_curve)
        models.Point(x=360, y=216, curve=bri_curve)
        models.Point(x=660, y=182, curve=bri_curve)
        models.Point(x=900, y=221, curve=bri_curve)
        models.Point(x=1080, y=27, curve=bri_curve)
        models.Point(x=1440, y=12, last=True, curve=bri_curve)
        db.add(bri_curve)

    ct_curve = crud.curve.get_default_by_kind(db, kind='ct')
    if not ct_curve:
        ct_curve = models.Curve(name='Default', kind='ct', default=True)
        models.Point(x=0, y=153, first=True, curve=ct_curve)
        models.Point(x=420, y=324, curve=ct_curve)
        models.Point(x=900, y=347, curve=ct_curve)
        models.Point(x=1080, y=475, curve=ct_curve)
        models.Point(x=1440, y=500, last=True, curve=ct_curve)
        db.add(ct_curve)

    db.commit()
    db.close()


if __name__ == '__main__':
    init()
