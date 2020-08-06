from app import models
from app.database import SessionLocal, engine


def init():
    db = SessionLocal()

    models.Base.metadata.create_all(bind=engine)

    status = db.query(models.Status).first()
    if not status:
        status = models.Status(id=0, status=False)
        db.add(status)

    settings = db.query(models.Settings).first()
    if not settings:
        settings = models.Settings(id=0, smart_off=True)
        db.add(settings)

    bri_curve = (db.query(models.Curve)
                   .filter_by(default=True)
                   .filter_by(kind='bri')
                   .first())
    if not bri_curve:
        bri_curve = models.Curve(name='Default', kind='bri', default=True)
        models.Point(x=0, y=245, first=True, curve=bri_curve)
        models.Point(x=360, y=216, curve=bri_curve)
        models.Point(x=660, y=182, curve=bri_curve)
        models.Point(x=900, y=221, curve=bri_curve)
        models.Point(x=1080, y=27, curve=bri_curve)
        models.Point(x=1440, y=12, last=True, curve=bri_curve)
        db.add(bri_curve)

    ct_curve = (db.query(models.Curve)
                  .filter_by(default=True)
                  .filter_by(kind='ct')
                  .first())
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
