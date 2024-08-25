from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..models.employee import Employee
from ..models.shift import Shift
from ..models import get_db
from datetime import time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse("index.html", {"request": request, "employees": employees})

@router.get("/shift-creation", response_class=HTMLResponse)
async def shift_creation_page(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    shifts = db.query(Shift).all()
    return templates.TemplateResponse("shift_creation.html", {"request": request, "employees": employees, "shifts": shifts, "time": time})