import logging
from sqlalchemy.orm import Session
from .models.employee import Employee
from .models.shift import Shift
from datetime import datetime, timedelta, time

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def assign_shifts(shift_type, shift_start_time, shift_end_time, current_date, available_employees, db, shifts):
    current_shift_start = shift_start_time
    current_shift_end = shift_end_time
    assigned_employees = []

    while current_shift_start != current_shift_end and available_employees:
        employee = available_employees.pop(0)
        request = next((r for r in employee.shift_requests if r.date == current_date.date()), None)
        logger.info(f"Date: {current_date.date()} - Processing employee: {employee.name}, Request: {request}")

        if request:
            # 1. request.start_time が current_shift_start の場合
            if request.start_time == current_shift_start:
                # ここに処理を追加
                start_datetime = datetime.combine(current_date, current_shift_start)
                end_datetime = datetime.combine(current_date, min(request.end_time, current_shift_end))

                requested_hours = max(0, (end_datetime - start_datetime).seconds // 3600)
                shift_hours = min(requested_hours, 5)
                logger.info(f"Date: {current_date.date()} - Calculated shift hours for {employee.name}: {shift_hours}")

                if shift_hours >= 3:
                    new_shift = Shift(
                        employee_id=employee.id,
                        date=current_date.date(),
                        start_time=start_datetime.time(),
                        end_time=(start_datetime + timedelta(hours=shift_hours)).time(),
                        shift_type=shift_type
                    )
                    shifts.append(new_shift)
                    db.add(new_shift)
                    current_shift_start = (start_datetime + timedelta(hours=shift_hours)).time()
                    assigned_employees.append(employee)
                    logger.info(f"Date: {current_date.date()} - Assigned {employee.name} to {shift_type} shift")

            # 2. request.end_time が current_shift_end の場合
            elif request.end_time == current_shift_end:
                # ここに処理を追加
                start_datetime = datetime.combine(current_date, max(request.start_time, current_shift_start))
                end_datetime = datetime.combine(current_date, current_shift_end)

                # end_datetime の値をログに出力
                logger.info(f"Date: {current_date.date()} - Calculated end_datetime: {end_datetime}")

                requested_hours = max(0, (end_datetime - start_datetime).seconds // 3600)
                shift_hours = min(requested_hours, 5)
                logger.info(f"Date: {current_date.date()} - Calculated shift hours for {employee.name}: {shift_hours}")

                if shift_hours >= 3:
                    new_shift = Shift(
                        employee_id=employee.id,
                        date=current_date.date(),
                        start_time=(end_datetime - timedelta(hours=shift_hours)).time(),
                        end_time=end_datetime.time(),
                        shift_type=shift_type
                    )
                    shifts.append(new_shift)
                    db.add(new_shift)
                    current_shift_end = (end_datetime - timedelta(hours=shift_hours)).time()
                    assigned_employees.append(employee)
                    logger.info(f"Date: {current_date.date()} - Assigned {employee.name} to {shift_type} shift")

            # 3. それ以外の場合
            else:
                # ここに処理を追加
                continue

    # 残りの時間帯を埋める
    if current_shift_start < shift_end_time:
        new_shift = Shift(
            employee_id=None,
            date=current_date.date(),
            start_time=current_shift_start,
            end_time=shift_end_time,
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)
    

    logger.info(f"Date: {current_date.date()} - Assigned employees for {shift_type} shift: {[e.name for e in assigned_employees]}")
    return assigned_employees

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
        # シフト希望を出している従業員をリストでまとめる
        available_employees = [e for e in employees if any(r.date == current_date.date() for r in e.shift_requests)]
        logger.info(f"Date: {current_date.date()} - Available employees for A shift: {[e.name for e in available_employees]}")

        # A枠を埋める
        assigned_employees = assign_shifts('A', time(15, 0), time(23, 0), current_date, available_employees, db, shifts)

        # A枠で割り当てた従業員をリストから削除
        available_employees = [e for e in employees if any(r.date == current_date.date() for r in e.shift_requests) and e not in assigned_employees]
        logger.info(f"Date: {current_date.date()} - Available employees for B shift: {[e.name for e in available_employees]}")

        # B枠を埋める
        assign_shifts('B', time(15, 0), time(23, 0), current_date, available_employees, db, shifts)

        current_date += delta

    db.commit()
    return shifts