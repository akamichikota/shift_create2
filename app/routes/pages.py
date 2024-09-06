from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models.employee import Employee
from ..models.shift import Shift, ShiftPeriod
from ..models import get_db
from datetime import datetime, timedelta, time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_shift_dates(start_date, end_date):
    current_date = start_date
    shift_dates = []
    while current_date <= end_date:
        shift_dates.append(current_date)
        current_date += timedelta(days=1)
    return shift_dates

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    shift_period = db.query(ShiftPeriod).first()
    shift_dates = get_shift_dates(shift_period.start_date, shift_period.end_date) if shift_period else []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "employees": employees,
        "shift_dates": shift_dates,
        "shift_period": shift_period,
    })

@router.get("/shift-creation", response_class=HTMLResponse)
async def shift_creation_page(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    shifts = db.query(Shift).all()
    shift_period = db.query(ShiftPeriod).first()
    shift_dates = get_shift_dates(shift_period.start_date, shift_period.end_date) if shift_period else []
    return templates.TemplateResponse("shift_creation.html", {
        "request": request,
        "employees": employees,
        "shifts": shifts,
        "shift_dates": shift_dates,
        "time": time
    })