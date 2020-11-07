from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.schedules import run
from app.api import get_api, ServerSession

router = APIRouter()


@router.get('/', response_model=List[schemas.Curve])
async def get_all_curves(
    kind: str = None,
    db: Session = Depends(get_db)
) -> Any:
    if kind:
        curves = crud.curve.get_multi_by_kind(db, kind=kind)
    else:
        curves = crud.curve.get_multi(db)
    return curves


@router.post('/', response_model=schemas.Curve)
async def create_curve(
    curve_in: schemas.CurveCreate,
    db: Session = Depends(get_db)
) -> Any:
    return crud.curve.create(db, obj_in=curve_in)


@router.get('/{id}', response_model=schemas.Curve)
async def get_curve(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    return crud.curve.get(db, id=id)


@router.put('/{id}', response_model=schemas.Curve)
async def update_curve(
    id: int,
    curve_in: schemas.CurveUpdate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    curve = crud.curve.get(db, id=id)
    curve = crud.curve.update(db, db_obj=curve, obj_in=curve_in)
    run(disable=True, db=db, api=api)
    return curve


@router.delete('/{id}', response_model=schemas.Curve)
async def delete_curve(
    id: int,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    curve = crud.curve.remove(db, id=id)
    run(disable=True, db=db, api=api)
    return curve


@router.post('/{id}/{point_index}', response_model=schemas.Curve)
async def insert_point(
    id: int,
    point_index: int,
    point_in: schemas.PointCreate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    curve = crud.curve.get(db, id=id)
    curve = crud.curve.create_point(
        db,
        curve=curve,
        point_index=point_index,
        point_in=point_in
    )
    run(disable=True, db=db, api=api)
    return curve


@router.delete('/{id}/{point_index}', response_model=schemas.Curve)
async def delete_point(
    id: int,
    point_index: int,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    curve = crud.curve.get(db, id=id)
    curve = crud.curve.delete_point(db, curve=curve, index=point_index)
    run(disable=True, db=db, api=api)
    return curve


@router.put('/{id}/{point_index}', response_model=schemas.Curve)
async def update_point(
    id: int,
    point_index: int,
    point_in: schemas.PointUpdate,
    db: Session = Depends(get_db),
    api: ServerSession = Depends(get_api)
) -> Any:
    curve = crud.curve.get(db, id=id)
    curve = crud.curve.update_point(
        db,
        curve=curve,
        index=point_index,
        point_in=point_in
    )
    run(disable=True, db=db, api=api)
    return curve
