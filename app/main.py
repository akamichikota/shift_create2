from fastapi import FastAPI, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .routes.employee import router as employee_router
from .routes.shift import router as shift_router
from .models.employee import Employee
from .models.shift import Shift
from .models import get_db
from .shift_scheduler import create_shifts

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(employee_router, prefix="/employee")
app.include_router(shift_router, prefix="/shift")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse("index.html", {"request": request, "employees": employees})

@app.get("/shift-creation", response_class=HTMLResponse)
async def shift_creation_page(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    shifts = db.query(Shift).all()
    return templates.TemplateResponse("shift_creation.html", {"request": request, "employees": employees, "shifts": shifts})

@app.post("/create_shifts")
async def create_shifts_endpoint(db: Session = Depends(get_db)):
    shifts = create_shifts(db)
    return RedirectResponse(url="/shift-creation", status_code=303)
