from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, and_, or_

from app.model import Roll
from app.validation import RollCreate


def create_roll(db: Session, roll: RollCreate):
    try:
        db_roll = Roll(**roll.model_dump())
        db.add(db_roll)
        db.commit()
        db.refresh(db_roll)
        return db_roll
    except ValidationError as msg:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(msg))
    except SQLAlchemyError as msg:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(msg))


def delete_roll(db: Session, roll_id: int):
    try:
        db_roll = db.query(Roll).filter(Roll.id == roll_id).first()
        if db_roll:
            db.delete(db_roll)
            db.commit()
            return db_roll
        return None
    except ValidationError as msg:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(msg))
    except SQLAlchemyError as msg:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(msg))


def select_with_filter(db: Session, id_min: Optional[int] = None,
                       id_max: Optional[int] = None,
                       lenght_min: Optional[float] = None,
                       lenght_max: Optional[float] = None,
                       weight_min: Optional[float] = None,
                       weight_max: Optional[float] = None,
                       added_date_min: Optional[date] = None,
                       added_date_max: Optional[date] = None,
                       removed_date_min: Optional[date] = None,
                       removed_date_max: Optional[date] = None):
    try:
        result = db.query(Roll)

        if id_min is not None:
            result = result.filter(Roll.id >= id_min)
        if id_max is not None:
            result = result.filter(Roll.id <= id_max)

        if lenght_min is not None:
            result = result.filter(Roll.length >= lenght_min)
        if lenght_max is not None:
            result = result.filter(Roll.length <= lenght_max)

        if weight_min is not None:
            result = result.filter(Roll.weight >= weight_min)
        if weight_max is not None:
            result = result.filter(Roll.weight <= weight_max)

        if added_date_min is not None:
            result = result.filter(Roll.added_date >= added_date_min)
        if added_date_max is not None:
            result = result.filter(Roll.added_date <= added_date_max)

        if removed_date_min is not None:
            result = result.filter(Roll.added_date >= removed_date_min)
        if removed_date_max is not None:
            result = result.filter(Roll.added_date <= removed_date_max)

        return result.all()
    except SQLAlchemyError as msg:
        raise HTTPException(status_code=500, detail=str(msg))


def get_stats(db: Session, begin_date: date, end_date: date):
    period = and_(Roll.added_date <= end_date,
                  or_(Roll.removed_date >= begin_date,
                      Roll.removed_date.is_(None)))
    query = db.query(
        func.count().filter(Roll.added_date.between(
            begin_date, end_date)).label("number_of_additions"),
        func.count().filter(Roll.removed_date.between(
            begin_date, end_date)).label("number_of_deletions"),
        func.avg(Roll.length).filter(period).label("average_lenght"),
        func.avg(Roll.weight).filter(period).label("average_weight"),
        func.max(Roll.length).filter(period).label("max_length"),
        func.min(Roll.length).filter(period).label("min_length"),
        func.max(Roll.weight).filter(period).label("max_weight"),
        func.min(Roll.weight).filter(period).label("min_weight"),
        func.sum(Roll.weight).filter(period).label("sum_weight"),
        func.max(Roll.removed_date - Roll.added_date).filter(
            period).label("max_period"),
        func.min(Roll.removed_date - Roll.added_date).filter(
            period).label("min_period")).first()

    days = [begin_date + timedelta(days=i) for i in range(
        (end_date - begin_date).days + 1)]

    counts = []
    for day in days:
        count = db.query(
            func.count()).filter(
            and_(Roll.added_date <= day,
                 or_(Roll.removed_date >= day,
                     Roll.removed_date.is_(None)))).scalar()
        counts.append((day, count))

    min_count = min(counts, key=lambda x: x[1])[1]
    max_count = max(counts, key=lambda x: x[1])[1]

    min_count_days = [day for day, count in counts if count == min_count]
    max_count_days = [day for day, count in counts if count == max_count]

    sums = []
    for day in days:
        count = db.query(
            func.sum(Roll.weight)).filter(
            and_(Roll.added_date <= day,
                 or_(Roll.removed_date >= day,
                     Roll.removed_date.is_(None)))).scalar()
        sums.append((day, count))

    min_weight = min(sums, key=lambda x: x[1])[1]
    max_weight = max(sums, key=lambda x: x[1])[1]

    min_weight_days = [day for day, weight in sums if weight == min_weight]
    max_weight_days = [day for day, weight in sums if weight == max_weight]

    if query is None:
        raise HTTPException(status_code=404, detail="Couldn't get statistics")

    return {"added_count": query.number_of_additions,
            "removed_count": query.number_of_deletions,
            "average_lenght": query.average_lenght,
            "average_weight": query.average_weight,
            "max_length": query.max_length,
            "min_length": query.min_length,
            "max_weight": query.max_weight,
            "min_weight": query.min_weight,
            "sum_weight": query.sum_weight,
            "max_duration": query.max_period,
            "min_duration": query.min_period,
            "min_count_day": min_count_days[0],
            "max_count_day": max_count_days[0],
            "min_weight_day": min_weight_days[0],
            "max_weight_day": max_weight_days[0]}
