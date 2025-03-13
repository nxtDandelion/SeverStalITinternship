import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import JSONResponse
from app.model import engine
from app.operations import create_roll, delete_roll, get_stats, select_with_filter
from app.validation import RollValid, RollCreate, RollStats, RollFilterParams

app = FastAPI()
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/rolls/create/", response_model=RollValid)
def create_roll_(roll: RollCreate, db: Session = Depends(get_db)):
    return create_roll(db, roll)


@app.delete("/rolls/delete/{roll_id}", response_model=RollValid)
def delete_roll_(roll_id: int, db: Session = Depends(get_db)):
    db_roll = delete_roll(db, roll_id)
    if db_roll is None:
        raise HTTPException(status_code=404,
                            detail="Roll with this id doesn't exist")
    return db_roll


@app.get("/rolls/", response_model=list[RollValid])
def get_filtered_rolls_(filters: RollFilterParams = Depends(),
                        db: Session = Depends(get_db)):
    return select_with_filter(db, id_min=filters.id_min,
                              id_max=filters.id_max,
                              lenght_min=filters.lenght_min,
                              lenght_max=filters.lenght_max,
                              weight_min=filters.weight_min,
                              weight_max=filters.weight_max,
                              added_date_min=filters.added_date_min,
                              added_date_max=filters.added_date_max,
                              removed_date_min=filters.removed_date_min,
                              removed_date_max=filters.removed_date_max)


@app.post("/rolls/stats/")
def get_stats_(req: RollStats, db: Session = Depends(get_db)):
    try:
        stats = get_stats(db, req.begin_date, req.end_date)
        return stats
    except OperationalError as msg:
        raise HTTPException(status_code=503, detail=msg)


@app.exception_handler(OperationalError)
async def database_error_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"message": "DataBase is unavailable"})


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Validation Error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail})


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
