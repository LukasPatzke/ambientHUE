from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.interpolate import monospline
import datetime as dt

router = APIRouter()


@router.get('/', response_model=List[schemas.Curve])
async def get_all_curves(
  db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Curve).all()


@router.post('/', response_model=schemas.Curve)
async def create_curve(
    curve_in: schemas.CurveCreate,
    db: Session = Depends(get_db)
) -> Any:
    curve = models.Curve(
        name=curve_in.name,
        kind=curve_in.kind,
        offset=curve_in.offset,
        default=False
    )
    models.Point(x=0, y=150, first=True, curve=curve)
    models.Point(x=1440, y=150, last=True, curve=curve)
    db.add(curve)
    db.commit()
    return curve


@router.get('/{id}', response_model=schemas.Curve)
async def get_curve(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.Curve).get(id)


@router.put('/{id}', response_model=schemas.Curve)
async def update_curve(
    id: int,
    curve_in: schemas.CurveCreate,
    db: Session = Depends(get_db)
) -> Any:
    curve = db.query(models.Curve).get(id)
    for attr, value in curve_in.items():
        setattr(curve, attr, value)

    db.commit()
    return curve


@router.delete('/{id}', response_model=schemas.Curve)
async def delete_curve(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    curve = db.query(models.Curve).get(id)
    if curve.default:
        raise HTTPException(
            status_code=422,
            detail='Default curves are not deletable'
        )
    db.delete(curve)
    db.commit()
    return curve


@router.post('/{id}/{pointIndex}', response_model=schemas.Curve)
async def insert_point(
    id: int,
    point_index: int,
    point_in: schemas.PointCreate,
    db: Session = Depends(get_db)
) -> Any:
    curve = db.query(models.Curve).get(id)
    points = (db.query(models.Point)
                .with_parent(curve)
                .order_by(models.Point.x)
                .all())

    point = points[point_index]

    if point_in.position == 'after':
        if point.last:
            raise HTTPException(
                status_code=422,
                detail='Can not create Point after last Point'
            )
        new_x = calc_new_point_location(
            before=points[point_index],
            after=points[point_index + 1]
        )
    else:
        if point.first:
            raise HTTPException(
                status_code=422,
                detail='Can not create Point before first Point'
            )
        new_x = calc_new_point_location(
            before=points[point_index-1],
            after=points[point_index]
        )

    models.Point(
        x=new_x,
        y=calc_curve_value(db, curve, new_x),
        curve=curve
    )

    db.commit()
    return db.query(models.Curve).get(id)


@router.delete('/{id}/{pointIndex}', response_model=schemas.Curve)
async def delete_point(
    id: int,
    point_index: int,
    db: Session = Depends(get_db)
) -> Any:
    curve = db.query(models.Curve).get(id)
    points = (db.query(models.Point)
                .with_parent(curve)
                .order_by(models.Point.x)
                .all())

    point = points[point_index]

    if point.first:
        raise HTTPException(
            status_code=422,
            detail='First Point is not deletable'
        )
    if point.last:
        raise HTTPException(
            status_code=422,
            detail='Last Point is not deletable'
        )
    db.delete(point)
    db.commit()
    return db.query(models.Curve).get(id)


@router.put('/{id}/{pointIndex}', response_model=schemas.Curve)
async def update_point(
    id: int,
    point_index: int,
    point_in: schemas.PointUpdate,
    db: Session = Depends(get_db)
) -> Any:
    curve = db.query(models.Curve).get(id)
    points = (db.query(models.Point)
                .with_parent(curve)
                .order_by(models.Point.x)
                .all())

    point = points[point_index]

    point.x = point_in.x
    point.y = point_in.y

    db.commit()
    return db.query(models.Curve).get(id)


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


def calc_new_point_location(
    before: schemas.Point,
    after: schemas.Point
) -> int:
    """ Calculate the location of a new point between two existing points """
    delta = abs(before.x - after.x)
    basis = min([before.x, after.x])
    return basis + delta/2
