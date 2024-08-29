from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.shift import ShiftRequest, Shift, ShiftPeriod
from ..models import get_db
from ..models.employee import Employee
from fastapi.responses import RedirectResponse
from ..shift_scheduler import create_shifts

router = APIRouter()

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

@router.post("/create_shifts")
async def create_shifts_endpoint(db: Session = Depends(get_db)):
    # データベースからシフト期間を取得
    shift_period = db.query(ShiftPeriod).first()
    if not shift_period:
        raise HTTPException(status_code=404, detail="シフト期間が設定されていません")

    start_date = shift_period.start_date
    end_date = shift_period.end_date

    # シフトを作成
    shifts = create_shifts(db, start_date, end_date)
    return RedirectResponse(url="/shift-creation", status_code=303)

@router.post("/set-shift-period")
async def set_shift_period(
    start_date: str = Form(...),
    end_date: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # 既存のシフト期間を削除
        db.query(ShiftPeriod).delete()

        # 新しいシフト期間を追加
        new_shift_period = ShiftPeriod(
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
        )
        db.add(new_shift_period)
        db.commit()
        db.refresh(new_shift_period)
        return {"message": "シフト期間が正常に設定されました。", "start_date": new_shift_period.start_date, "end_date": new_shift_period.end_date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"シフト期間の設定中にエラーが発生しました: {str(e)}")

@router.get("/shift-period")
async def get_shift_period(db: Session = Depends(get_db)):
    shift_period = db.query(ShiftPeriod).first()
    if not shift_period:
        return {"start_date": None, "end_date": None}
    return {"start_date": shift_period.start_date, "end_date": shift_period.end_date}