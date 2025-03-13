from datetime import date
from typing import Optional
from pydantic import BaseModel, PositiveFloat, PositiveInt


class RollBase(BaseModel):
    length: PositiveFloat
    weight: PositiveFloat


class RollValid(RollBase):
    id: int
    added_date: date
    removed_date: Optional[date]

    class Config:
        from_attributes = True


class RollCreate(RollBase):
    added_date: Optional[date] = None
    removed_date: Optional[date] = None


class RollFilterParams(BaseModel):
    id_min: Optional[PositiveInt] = None
    id_max: Optional[PositiveInt] = None
    lenght_min: Optional[PositiveFloat] = None
    lenght_max: Optional[PositiveFloat] = None
    weight_min: Optional[PositiveFloat] = None
    weight_max: Optional[PositiveFloat] = None
    added_date_min: Optional[date] = None
    added_date_max: Optional[date] = None
    removed_date_min: Optional[date] = None
    removed_date_max: Optional[date] = None


class RollStats(BaseModel):
    begin_date: date
    end_date: date
