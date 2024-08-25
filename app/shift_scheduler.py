from sqlalchemy.orm import Session
from .models.employee import Employee
from .models.shift import Shift, ShiftRequest
from datetime import datetime, timedelta
import random

def create_shifts(db: Session):
    # 既存のシフトを削除
    db.query(Shift).delete()
    
    employees = db.query(Employee).all()
    shifts = []

    # シフトを作成する日付の範囲を設定
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 8, 15)
    delta = timedelta(days=1)

    current_date = start_date
    while current_date <= end_date:
        # ランダムに従業員を選択
        available_employees = [e for e in employees if any(r.date == current_date.date() for r in e.shift_requests)]
        if available_employees:
            selected_employee = random.choice(available_employees)
            request = next(r for r in selected_employee.shift_requests if r.date == current_date.date())
            new_shift = Shift(
                employee_id=selected_employee.id,
                date=request.date,
                start_time=request.start_time,
                end_time=request.end_time
            )
            shifts.append(new_shift)
            db.add(new_shift)
        current_date += delta

    db.commit()
    return shifts