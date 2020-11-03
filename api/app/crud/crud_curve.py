from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
import datetime as dt
from functools import lru_cache

from app.crud.base import CRUDBase
from app.models import Curve, Point
from app import schemas

from app.interpolate import monospline


class CRUDCurve(CRUDBase[Curve, schemas.CurveCreate, schemas.CurveUpdate]):
    def get_multi_by_kind(
        self,
        db: Session,
        kind: str,
    ) -> List[Curve]:
        return db.query(Curve).filter_by(kind=kind).all()

    def get_default_by_kind(
        self,
        db: Session,
        kind: str,
    ) -> List[Curve]:
        return (db.query(Curve)
                  .filter_by(default=True)
                  .filter_by(kind=kind)
                  .first())

    def create(
        self,
        db: Session,
        *,
        curve_in: schemas.CurveCreate
    ) -> Curve:
        obj_in_data = jsonable_encoder(curve_in)
        db_obj = self.model(**obj_in_data, default=False)  # type: ignore

        Point(x=0, y=200, first=True, curve=curve)
        Point(x=1440, y=200, last=True, curve=curve)
        for index in range(1, curve_in.count - 1):
            Point(
                x=1440/(curve_in.count - 1) * index,
                y=200,
                curve=db_obj
            )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Curve:
        obj = db.query(self.model).get(id)
        if obj.default:
            raise HTTPException(
                status_code=422,
                detail='Default curves are not deletable'
            )
        db.delete(obj)
        db.commit()
        return obj

    def get_point(
        self,
        db: Session,
        curve: Curve,
        index: int
    ) -> List[Point]:
        points = (db.query(Point)
                    .with_parent(curve)
                    .order_by(Point.x)
                    .all())

        return points[index]

    def get_multiple_points(
        self,
        db: Session,
        curve: Curve
    ) -> List[Point]:
        return (db.query(Point)
                .with_parent(curve)
                .order_by(Point.x)
                .all())

    def create_point(
        self,
        db: Session,
        *,
        curve: Curve,
        point_index: int,
        point_in: schemas.PointCreate
    ) -> Curve:
        points = self.get_multiple_points(db, curve=curve)
        point = points[point_index]

        if point_in.position == 'after':
            if point.last:
                raise HTTPException(
                    status_code=422,
                    detail='Can not create Point after last Point'
                )
            new_x = self.new_point_location(
                before=points[point_index],
                after=points[point_index + 1]
            )
        else:
            if point.first:
                raise HTTPException(
                    status_code=422,
                    detail='Can not create Point before first Point'
                )
            new_x = self.new_point_location(
                before=points[point_index-1],
                after=points[point_index]
            )

        Point(
            x=new_x,
            y=self.calc_value(db, curve, new_x),
            curve=curve
        )
        db.commit()
        db.refresh(curve)
        return curve

    def delete_point(
        self,
        db: Session,
        *,
        curve: Curve,
        index: int
    ) -> Curve:
        point = self.get_point(db, curve=curve, index=index)

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
        db.refresh(curve)
        return curve

    def update_point(
        self,
        db: Session,
        *,
        curve: Curve,
        index: int,
        point_in: schemas.PointUpdate
    ) -> Curve:
        point = self.get_point(db, curve=curve, index=index)

        point.x = point_in.x
        point.y = point_in.y

        db.commit()
        db.refresh(curve)
        return curve

    @lru_cache()
    def calc_value(
        self,
        db: Session,
        curve: schemas.Curve,
        x: Optional[int] = None
    ) -> int:
        """ Calculate the value from the points"""
        points = self.get_multiple_points(db, curve=curve)

        if x is None:
            now = dt.datetime.now()
            day_start = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            x = int((now - day_start).total_seconds() / 60) - 4*60

        cs = monospline(
            xs=[point.x for point in points],
            ys=[point.y + curve.offset for point in points],
        )

        value = int(cs(x))
        return value

    def new_point_location(
        self,
        before: schemas.Point,
        after: schemas.Point
    ) -> int:
        """ Calculate the location of a new point between two existing
        points """
        delta = abs(before.x - after.x)
        basis = min([before.x, after.x])
        return basis + delta/2


curve = CRUDCurve(Curve)
