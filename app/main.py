from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes.employee import router as employee_router
from .routes.shift import router as shift_router
from .routes.pages import router as pages_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(employee_router, prefix="/employee")
app.include_router(shift_router, prefix="/shift")
app.include_router(pages_router)