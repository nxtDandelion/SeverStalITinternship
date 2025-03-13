from sqlalchemy import Column, Integer, Float, Date, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import ArgumentError
from app.config import settings


class DB(DeclarativeBase):
    pass


if settings.db_url is None:
    raise ValueError("DB_URL is not set in settings")

try:
    engine = create_engine(settings.db_url, echo=True)
except ArgumentError as msg:
    raise ValueError(msg)


class Roll(DB):
    __tablename__ = "rolls"
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    added_date = Column(Date, default=func.current_date())
    removed_date = Column(Date, nullable=True)
