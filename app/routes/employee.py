from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.employee import Employee
from ..models.shift import ShiftRequest
from ..models import get_db, SessionLocal
from pydantic import BaseModel

router = APIRouter()

# データベースセッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class EmployeeUpdate(BaseModel):
    name: str
    weekly_shifts: int

@router.post("/create-employee")
async def create_employee(
    name: str = Form(...),
    weekly_shifts: int = Form(...),
    db: Session = Depends(get_db)
):
    new_employee = Employee(name=name, weekly_shifts=weekly_shifts)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return {"message": "従業員が正常に作成されました。", "id": new_employee.id}

@router.post("/delete-employee/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="従業員が見つかりません")
    
    # 関連するシフト希望を削除
    db.query(ShiftRequest).filter(ShiftRequest.employee_id == employee_id).delete()
    
    db.delete(employee)
    db.commit()
    return {"message": "従業員が削除されました"}

@router.post("/edit-employee/{employee_id}")
async def edit_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="従業員が見つかりません")

    employee.name = employee_update.name
    employee.weekly_shifts = employee_update.weekly_shifts
    db.commit()
    return {"message": "従業員情報が更新されました"}