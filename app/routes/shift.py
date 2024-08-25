from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.shift import ShiftRequest
from ..models import get_db
from ..models.employee import Employee
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/add-shift-request")
async def add_shift_request(
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.json()
    employee_id = data['employee_id']
    shift_requests = data['shift_requests']

    for shift in shift_requests:
        date_obj = datetime.strptime(shift['date'], "%Y-%m-%d").date()
        start_time_obj = datetime.strptime(shift['start_time'], "%H:%M").time()
        end_time_obj = datetime.strptime(shift['end_time'], "%H:%M").time()

        new_shift_request = ShiftRequest(
            employee_id=employee_id,
            date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj
        )
        db.add(new_shift_request)

    db.commit()
    return {"message": "シフト希望が正常に追加されました。"}

@router.post("/delete-shift-request/{shift_request_id}")
async def delete_shift_request(shift_request_id: int, db: Session = Depends(get_db)):
    shift_request = db.query(ShiftRequest).filter(ShiftRequest.id == shift_request_id).first()
    if not shift_request:
        raise HTTPException(status_code=404, detail="シフト希望が見つかりません")
    db.delete(shift_request)
    db.commit()
    return {"message": "シフト希望が削除されました"}

@router.get("/shift-creation", response_class=HTMLResponse)
async def shift_creation_page(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse("shift_creation.html", {"request": request, "employees": employees})

