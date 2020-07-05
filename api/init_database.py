from app import models
from app.database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

status = models.Status(
    id=0,
    status=False
)

ct_curve = models.Curve(name='Default', kind='ct', default=True)
models.Point(x=0, y=153, first=True, curve=ct_curve)
models.Point(x=400, y=160, curve=ct_curve)
models.Point(x=800, y=240, curve=ct_curve)
models.Point(x=1200, y=300, curve=ct_curve)
models.Point(x=1440, y=450, last=True, curve=ct_curve)

bri_curve = models.Curve(name='Default', kind='bri', default=True)
models.Point(x=0, y=254, first=True, curve=bri_curve)
models.Point(x=400, y=200, curve=bri_curve)
models.Point(x=800, y=150, curve=bri_curve)
models.Point(x=1200, y=100, curve=bri_curve)
models.Point(x=1440, y=50, last=True, curve=bri_curve)

db.add(ct_curve)
db.add(bri_curve)

db.add(status)
db.commit()
db.close()
