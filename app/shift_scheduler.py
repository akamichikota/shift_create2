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
        request = next((r for r in employee.shift_requests if r.date == current_date), None)
        logger.info(f"Date: {current_date} - Processing employee: {employee.name}, Request: {request}")

        if request:
            if request.start_time == current_shift_start and (current_shift_end == shift_end_time or request.end_time >= current_shift_end):
                assigned_employees, shift_hours = process_shift_request(
                    employee, request, 'first', current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                logger.info(f"Before update: {current_shift_start}")
                current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
                logger.info(f"After update: {current_shift_start}")
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

            elif request.end_time == current_shift_end and (current_shift_start == shift_start_time or request.start_time <= current_shift_start):
                assigned_employees, shift_hours = process_shift_request(
                    employee, request, 'second', current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                current_shift_end = (datetime.combine(current_date, current_shift_end) - timedelta(hours=shift_hours)).time()
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")
            
            elif ((current_shift_start == shift_start_time and current_shift_end == shift_end_time) and 
                  (max(0, (min(datetime.combine(datetime.today(), request.end_time), 
                  datetime.combine(datetime.today(), shift_end_time)) - 
                  max(datetime.combine(datetime.today(), request.start_time), 
                      datetime.combine(datetime.today(), shift_start_time))).total_seconds() // 3600) >= 3)):
                assigned_employees, shift_hours = process_shift_request(
                    employee, request, 'third', current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

    if current_shift_start < shift_end_time:
        new_shift = Shift(
            employee_id=None,
            date=current_date,
            start_time=current_shift_start,
            end_time=shift_end_time,
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)

    logger.info(f"Date: {current_date} - Assigned employees for {shift_type} shift: {[e.name for e in assigned_employees]}")
    return assigned_employees

def process_shift_request(employee, request, time_period, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    # request.start_time と request.end_time を datetime.datetime に変換
    request_start_datetime = datetime.combine(current_date, request.start_time)
    request_end_datetime = datetime.combine(current_date, request.end_time)

    # current_shift_start と current_shift_end を datetime.datetime に変換
    current_shift_start_datetime = datetime.combine(current_date, current_shift_start)
    current_shift_end_datetime = datetime.combine(current_date, current_shift_end)

    # 時間数を計算
    requested_hours = min(((current_shift_end_datetime - request_start_datetime).seconds // 3600), (request_end_datetime - current_shift_start_datetime).seconds // 3600)
    shift_hours = min(requested_hours, (current_shift_end_datetime - current_shift_start_datetime).seconds // 3600, 5)

    if time_period == 'first':
        start_datetime = request_start_datetime
    elif time_period == 'second':
        start_datetime = current_shift_end_datetime - timedelta(hours=shift_hours)
    elif time_period == 'third':
        start_datetime = max(request_start_datetime, current_shift_start_datetime)

    logger.info(f"Date: {current_date} - Calculated shift hours for {employee.name}: {shift_hours}")

    if shift_hours >= 3 and employee_shift_limits[employee.id] > 0:
        new_shift = Shift(
            employee_id=employee.id,
            date=current_date,
            start_time=start_datetime.time(),
            end_time=(start_datetime + timedelta(hours=shift_hours)).time(),
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)
        assigned_employees.append(employee)
        employee_shift_limits[employee.id] -= 1  # シフト希望日数を減少
        logger.info(f"Date: {current_date} - Assigned {employee.name} to {shift_type} shift")

    return assigned_employees, shift_hours  # タプルで返却

def create_shifts(db: Session, start_date: datetime, end_date: datetime):
    db.query(Shift).delete()
    
    employees = db.query(Employee).all()
    shifts = []

    current_date = start_date

    while current_date <= end_date:
        process_week_shifts(current_date, employees, db, shifts)
        current_date += timedelta(days=7)

    db.commit()
    return shifts

def process_week_shifts(current_date, employees, db, shifts):
    week_end_date = current_date + timedelta(days=6)

    remaining_shift_requests = {
        employee.id: sum(1 for r in employee.shift_requests if current_date <= r.date <= week_end_date)
        for employee in employees
    }

    date_employee_count = {
        current_date + timedelta(days=i): sum(1 for e in employees if any(r.date == (current_date + timedelta(days=i)) for r in e.shift_requests))
        for i in range((week_end_date - current_date).days + 1)
    }

    sorted_dates = sorted(date_employee_count.keys(), key=lambda d: date_employee_count[d])
    logger.info(f"Sorted dates for the week: {[date for date in sorted_dates]}")

    employee_shift_limits = {employee.id: employee.weekly_shifts for employee in employees}

    while sorted_dates:
        current_date = select_date_with_fewest_requests(sorted_dates, employees, employee_shift_limits)
        if not current_date:
            break
        
        # A枠の割り当て
        available_employees = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests)]
        available_employees.sort(key=lambda e: (
            remaining_shift_requests[e.id] - employee_shift_limits[e.id], 
            next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                 for r in e.shift_requests if r.date == current_date), 
            sum(
                (datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            )
        ))

        logger.info(f"Date: {current_date} - Available employees for A shift: {[e.name for e in available_employees]}")
        assigned_employees_A = assign_shifts('A', time(15, 0), time(23, 0), current_date, available_employees, db, shifts, employee_shift_limits)
        update_remaining_requests(assigned_employees_A, remaining_shift_requests)

        # B枠の割り当て
        available_employees = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests) and e not in assigned_employees_A]
        available_employees.sort(key=lambda e: (
            remaining_shift_requests[e.id] - employee_shift_limits[e.id],
            next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                 for r in e.shift_requests if r.date == current_date),
            sum(
                (datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            )
        ))

        logger.info(f"Date: {current_date} - Available employees for B shift: {[e.name for e in available_employees]}")
        assigned_employees_B = assign_shifts('B', time(15, 0), time(23, 0), current_date, available_employees, db, shifts, employee_shift_limits)
        update_remaining_requests(assigned_employees_B, remaining_shift_requests)

        # C枠の割り当て
        available_employees = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests) and e not in assigned_employees_A and e not in assigned_employees_B]
        shift_start_time = time(18, 0)
        shift_end_time = time(22, 0)
        available_employees.sort(key=lambda e: (
            # シフト希望時間帯との重複時間を計算
            sum(
                max(0, (min(datetime.combine(datetime.today(), r.end_time), datetime.combine(datetime.today(), shift_end_time)) - 
                          max(datetime.combine(datetime.today(), r.start_time), datetime.combine(datetime.today(), shift_start_time))).total_seconds() // 3600)
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            ),
            remaining_shift_requests[e.id] - employee_shift_limits[e.id],
            sum(
                (datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            )
        ))

        logger.info(f"Date: {current_date} - Available employees for C shift: {[e.name for e in available_employees]}")
        assigned_employees_C = assign_shifts('C', shift_start_time, shift_end_time, current_date, available_employees, db, shifts, employee_shift_limits)
        update_remaining_requests(assigned_employees_C, remaining_shift_requests)

        sorted_dates.remove(current_date)

def select_date_with_fewest_requests(sorted_dates, employees, employee_shift_limits):
    date_employee_count = {
        date: sum(1 for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == date for r in e.shift_requests))
        for date in sorted_dates
    }
    date_employee_count = {date: count for date, count in date_employee_count.items() if count > 0}
    if not date_employee_count:
        return None
    return min(date_employee_count, key=date_employee_count.get)

def update_remaining_requests(assigned_employees, remaining_shift_requests):
    for employee in assigned_employees:
        remaining_shift_requests[employee.id] -= 1