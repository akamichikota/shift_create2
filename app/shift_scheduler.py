import logging
from sqlalchemy.orm import Session
from .models.employee import Employee
from .models.shift import Shift
from datetime import datetime, timedelta, time
import random

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def assign_shifts(shift_type, shift_start_time, shift_end_time, current_date, available_employees, db, shifts, employee_shift_limits):
    current_shift_start = shift_start_time
    current_shift_end = shift_end_time
    assigned_employees = []

    while current_shift_start != current_shift_end and available_employees:
        employee = available_employees.pop(0)
        request = next((r for r in employee.shift_requests if r.date == current_date.date()), None)
        logger.info(f"Date: {current_date.date()} - Processing employee: {employee.name}, Request: {request}")

        if request:
            if request.start_time == current_shift_start and (current_shift_end == shift_end_time or request.end_time >= current_shift_end):
                start_datetime = datetime.combine(current_date, current_shift_start)
                end_datetime = datetime.combine(current_date, min(request.end_time, current_shift_end))

                requested_hours = max(0, (end_datetime - start_datetime).seconds // 3600)
                shift_hours = min(requested_hours, 5)
                logger.info(f"Date: {current_date.date()} - Calculated shift hours for {employee.name}: {shift_hours}")

                if shift_hours >= 3 and employee_shift_limits[employee.id] > 0:
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
                    employee_shift_limits[employee.id] -= 1  # シフト希望日数を減少
                    logger.info(f"Date: {current_date.date()} - Assigned {employee.name} to {shift_type} shift")

            elif request.end_time == current_shift_end and (current_shift_start == shift_start_time or request.start_time <= current_shift_start):
                start_datetime = datetime.combine(current_date, max(request.start_time, current_shift_start))
                end_datetime = datetime.combine(current_date, current_shift_end)

                logger.info(f"Date: {current_date.date()} - Calculated end_datetime: {end_datetime}")

                requested_hours = max(0, (end_datetime - start_datetime).seconds // 3600)
                shift_hours = min(requested_hours, 5)
                logger.info(f"Date: {current_date.date()} - Calculated shift hours for {employee.name}: {shift_hours}")

                if shift_hours >= 3 and employee_shift_limits[employee.id] > 0:
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
                    employee_shift_limits[employee.id] -= 1  # シフト希望日数を減少
                    logger.info(f"Date: {current_date.date()} - Assigned {employee.name} to {shift_type} shift")

            else:
                continue

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
    db.query(Shift).delete()
    
    employees = db.query(Employee).all()
    shifts = []

    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 8, 15)
    delta = timedelta(days=1)

    current_date = start_date

    while current_date <= end_date:
        # 一週間のシフト希望を処理
        week_end_date = current_date + timedelta(days=6)

        # 週の初めにremaining_shift_requestsをリセット
        remaining_shift_requests = {
            employee.id: sum(1 for r in employee.shift_requests if current_date.date() <= r.date <= week_end_date.date())
            for employee in employees
        }

        # 各従業員のシフト希望日数を追跡する辞書
        employee_shift_limits = {employee.id: employee.weekly_shifts for employee in employees}
        

        while current_date <= week_end_date and current_date <= end_date:
            # シフト希望を出している従業員をリストでまとめる
            available_employees = [e for e in employees if any(r.date == current_date.date() for r in e.shift_requests) and employee_shift_limits[e.id] > 0]
            
            # employee_shift_limitsとremaining_shift_requestsに基づいて並び替え
            available_employees.sort(key=lambda e: (remaining_shift_requests[e.id] - employee_shift_limits[e.id], 
                                                      next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                                                            for r in e.shift_requests if r.date == current_date.date()), 0))
            
            logger.info(f"Date: {current_date.date()} - Available employees for A shift: {[e.name for e in available_employees]}")

            # A枠を埋める
            assigned_employees = assign_shifts('A', time(15, 0), time(23, 0), current_date, available_employees, db, shifts, employee_shift_limits)

            # 割り当てた従業員の「シフト希望を出している日数の残り」を減少
            for employee in assigned_employees:
                remaining_shift_requests[employee.id] -= 1

            available_employees = [e for e in employees if any(r.date == current_date.date() for r in e.shift_requests) and e not in assigned_employees and employee_shift_limits[e.id] > 0]

            # employee_shift_limitsとremaining_shift_requestsに基づいて並び替え
            available_employees.sort(key=lambda e: (remaining_shift_requests[e.id] - employee_shift_limits[e.id], 
                                                      next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                                                            for r in e.shift_requests if r.date == current_date.date()), 0))
            
            logger.info(f"Date: {current_date.date()} - Available employees for B shift: {[e.name for e in available_employees]}")

            # B枠を埋める
            assigned_employees = assign_shifts('B', time(15, 0), time(23, 0), current_date, available_employees, db, shifts, employee_shift_limits)

            # その日にシフト希望を出していた全ての従業員の「シフト希望を出している日数の残り」を減少
            for employee in available_employees:
                if employee.id in remaining_shift_requests:
                    remaining_shift_requests[employee.id] -= 1

            current_date += delta

    db.commit()
    return shifts