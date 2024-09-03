import logging
from sqlalchemy.orm import Session
from .models.employee import Employee
from .models.shift import Shift
from datetime import datetime, timedelta, time
import random

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# シフトの時間設定
MIN_SHIFT_HOURS = 3  # 最低シフト時間
MAX_SHIFT_HOURS = 5  # 最高シフト時間

SHIFT_A_START = time(15, 0)  # Aシフトの開始時間
SHIFT_A_END = time(23, 0)    # Aシフトの終了時間
SHIFT_B_START = time(15, 0)  # Bシフトの開始時間
SHIFT_B_END = time(23, 0)    # Bシフトの終了時間
SHIFT_C_START = time(18, 0)  # Cシフトの開始時間
SHIFT_C_END = time(21, 0)    # Cシフトの終了時間

def assign_shifts(shift_type, assigned_shifts, employee_state, shift_start_time, shift_end_time, current_date, available_employees, db, shifts, employee_shift_limits):
    current_shift_start = shift_start_time
    current_shift_end = shift_end_time
    assigned_employees = []

    while current_shift_start != current_shift_end and available_employees:
        employee = available_employees.pop(0) if available_employees else None  # 修正
        if employee is None:  # 修正
            break  # 修正
        request = next((r for r in employee.shift_requests if r.date == current_date), None)
        logger.info(f"Date: {current_date} - Processing employee: {employee.name}, Request: {request}")

        if request:
            if (request.start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or request.end_time >= current_shift_end) and 
                employee_state == 'new' and
                # (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=MIN_SHIFT_HOURS)) and
                (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
                (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
                assigned_employees, shift_hours = process_shift_request(
                    employee, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                logger.info(f"Before update: {current_shift_start}")
                current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
                logger.info(f"After update: {current_shift_start}")
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

            elif (request.end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or request.start_time <= current_shift_start) and 
                employee_state == 'new' and
                # (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=MIN_SHIFT_HOURS)) and
                (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
                (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
                assigned_employees, shift_hours = process_shift_request(
                    employee, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                current_shift_end = (datetime.combine(current_date, current_shift_end) - timedelta(hours=shift_hours)).time()
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")


            
            elif (request.start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or request.end_time >= current_shift_end) and 
                employee_state == 'repeat' and
                (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=1)) and
                (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=1))):
                assigned_employees, shift_hours = process_shift_request(
                    employee, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                logger.info(f"Before update first最初: {current_shift_start}")
                logger.info(f"Before update first最後: {current_shift_end}")
                logger.info(f"Before update firstshift_hours: {shift_hours}")
                current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
                logger.info(f"After update: {current_shift_start}")
                logger.info(f"After update: {current_shift_end}")
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")
            
            elif (request.end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or request.start_time <= current_shift_start) and 
                employee_state == 'repeat' and
                (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=1)) and
                (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=1))):
                assigned_employees, shift_hours = process_shift_request(
                    employee, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
                )
                logger.info(f"Before update second最初: {current_shift_start}")
                logger.info(f"Before update second最後: {current_shift_end}")
                current_shift_end = (datetime.combine(current_date, current_shift_start) - timedelta(hours=shift_hours)).time()
                logger.info(f"After update: {current_shift_start}")
                logger.info(f"After update: {current_shift_end}")
                logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

    # デフォルト従業員のIDを取得
    default_employee = db.query(Employee).filter(Employee.name == "none").first()
    default_employee_id = default_employee.id if default_employee else None  # 従業員が見つからない場合は None

    if current_shift_start < current_shift_end:
        new_shift = Shift(
            employee_id=default_employee_id,  # ここを修正
            date=current_date,
            start_time=current_shift_start,
            end_time=current_shift_end,
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)

    logger.info(f"Date: {current_date} - Assigned employees for {shift_type} shift: {[e.name for e in assigned_employees]}")
    return assigned_employees


def process_shift_request(employee, assigned_shifts, employee_state, request, time_period, start_shift_time, end_shift_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    # request.start_time と request.end_time を datetime.datetime に変換
    request_start_datetime = datetime.combine(current_date, request.start_time)
    request_end_datetime = datetime.combine(current_date, request.end_time)
    shift_time = (datetime.combine(datetime.today(), end_shift_time) - datetime.combine(datetime.today(), start_shift_time)).seconds / 3600

    # current_shift_start と current_shift_end を datetime.datetime に変換
    current_shift_start_datetime = datetime.combine(current_date, current_shift_start)
    current_shift_end_datetime = datetime.combine(current_date, current_shift_end)

    # 時間数を計算 一個目だったらshift_timeと同じ
    requested_hours = min(((current_shift_end_datetime - request_start_datetime).seconds // 3600), (request_end_datetime - current_shift_start_datetime).seconds // 3600)
    
    if MAX_SHIFT_HOURS < shift_time < MAX_SHIFT_HOURS + MIN_SHIFT_HOURS:
        shift_minimum_time = shift_time - MIN_SHIFT_HOURS
    elif MAX_SHIFT_HOURS <= shift_time and (shift_time - requested_hours < MIN_SHIFT_HOURS) and requested_hours < shift_time:
        shift_minimum_time = shift_time - MIN_SHIFT_HOURS
    else:
        shift_minimum_time = MAX_SHIFT_HOURS
    
    shift_hours = min(requested_hours, (current_shift_end_datetime - current_shift_start_datetime).seconds // 3600, shift_minimum_time, MAX_SHIFT_HOURS)


    # リピートの時、二つとも入れる時と一つだけ入れる時で、スタートとエンドが変わるので、場合分けする。また、　Available employeesの順番でassigned_shifts_Aなどが入っているが、実際は、先にsecondで割り当てられているカモシカもしれないので、assigned_shifts[1]がどっちの従業員を指しているかは判別しづらい
    if time_period == 'first':
        start_datetime = current_shift_start_datetime
        start_datetime_repeat = current_shift_start_datetime
        if assigned_shifts and max(assigned_shifts[0]['shift_start'], assigned_shifts[1]['shift_start']) ==  (start_shift_time or end_shift_time):
            end_datetime_repeat = current_shift_end_datetime
        else:
            end_datetime_repeat = datetime.combine(current_date, max(assigned_shifts[0]['shift_start'], assigned_shifts[1]['shift_start'])) if len(assigned_shifts) > 1 else datetime.combine(current_date, end_shift_time)  # 修正
    elif time_period == 'second':
        start_datetime = current_shift_end_datetime - timedelta(hours=shift_hours)
        end_datetime_repeat = current_shift_end_datetime
        if assigned_shifts and min(assigned_shifts[0]['shift_end'], assigned_shifts[1]['shift_end']) == (start_shift_time or end_shift_time):
            start_datetime_repeat = current_shift_start_datetime
        else:
            start_datetime_repeat = datetime.combine(current_date, min(assigned_shifts[0]['shift_end'], assigned_shifts[1]['shift_end'])) if len(assigned_shifts) > 1 else datetime.combine(current_date, end_shift_time)  # 修正

    logger.info(f"Date: {current_date} - Calculated shift hours for {employee.name}: {shift_hours}")

    logger.info(f"Date: {current_date} - 開始時間{start_datetime_repeat}　終了時間{end_datetime_repeat}")
    logger.info(f"Date: {current_date} - 残りシフト可能回数{employee_shift_limits[employee.id]}")

    if employee_state == 'new' and employee_shift_limits[employee.id] > 0:
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

    elif employee_state == 'repeat':
        shift_hours = (end_datetime_repeat - start_datetime_repeat).seconds // 3600
        new_shift = Shift(
            employee_id=employee.id,
            date=current_date,
            start_time=start_datetime_repeat.time(),  # 修正
            end_time=end_datetime_repeat.time(),  # 修正
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)
        assigned_employees.append(employee)


        
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
        available_employees_A = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests)]

        if len(available_employees_A) > 1:
            random.shuffle(available_employees_A)
        
        available_employees_A.sort(key=lambda e: (
            remaining_shift_requests[e.id] - employee_shift_limits[e.id], 
            next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                 for r in e.shift_requests if r.date == current_date), 
            sum(
                (datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            )
        ))

















        logger.info(f"Date: {current_date} - Available employees for A shift: {[e.name for e in available_employees_A]}")
        assigned_employees_A = assign_shifts('A', [], 'new', SHIFT_A_START, SHIFT_A_END, current_date, available_employees_A, db, shifts, employee_shift_limits)
        assigned_shifts_A = []

        for employee in assigned_employees_A:
            # 各従業員のシフトリクエストを取得
            request = next((r for r in employee.shift_requests if r.date == current_date), None)
            
            # 実際に割り当てられたシフトの開始時間と終了時間を取得
            assigned_shift = next((s for s in shifts if s.employee_id == employee.id and s.date == current_date), None)
            
            if assigned_shift:
                assigned_shifts_A.append({
                    'employee_name': employee.name,
                    'shift_start': assigned_shift.start_time,  # 実際の開始時間
                    'shift_end': assigned_shift.end_time,      # 実際の終了時間
                    'requested_start': request.start_time if request else None,  # シフト希望開始時間
                    'requested_end': request.end_time if request else None       # シフト希望終了時間
                })

        update_remaining_requests(assigned_employees_A, remaining_shift_requests)



        # B枠の割り当て
        available_employees_B = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests) and e not in assigned_employees_A]

        if len(available_employees_B) > 1:
            random.shuffle(available_employees_B)
        
        available_employees_B.sort(key=lambda e: (
            remaining_shift_requests[e.id] - employee_shift_limits[e.id],
            next((datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600 
                 for r in e.shift_requests if r.date == current_date),
            sum(
                (datetime.combine(datetime.today(), r.end_time) - datetime.combine(datetime.today(), r.start_time)).seconds // 3600
                for r in e.shift_requests
                if r.date in [date for date in sorted_dates]
            )
        ))

        logger.info(f"Date: {current_date} - Available employees for B shift: {[e.name for e in available_employees_B]}")
        assigned_employees_B = assign_shifts('B', [], 'new', SHIFT_B_START, SHIFT_B_END, current_date, available_employees_B, db, shifts, employee_shift_limits)
        assigned_shifts_B = []

        for employee in assigned_employees_B:
            # 各従業員のシフトリクエストを取得
            request = next((r for r in employee.shift_requests if r.date == current_date), None)
            
            # 実際に割り当てられたシフトの開始時間と終了時間を取得
            assigned_shift = next((s for s in shifts if s.employee_id == employee.id and s.date == current_date), None)
            
            if assigned_shift:
                assigned_shifts_B.append({
                    'employee_name': employee.name,
                    'shift_start': assigned_shift.start_time,  # 実際の開始時間
                    'shift_end': assigned_shift.end_time,      # 実際の終了時間
                    'requested_start': request.start_time if request else None,  # シフト希望開始時間
                    'requested_end': request.end_time if request else None       # シフト希望終了時間
                })

        update_remaining_requests(assigned_employees_B, remaining_shift_requests)



        # C枠の割り当て
        available_employees_C = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests) and e not in assigned_employees_A and e not in assigned_employees_B]

        if len(available_employees_C) > 1:
            random.shuffle(available_employees_C)
        
        available_employees_C.sort(key=lambda e: (
            # シフト希望時間帯との重複時間を計算
            sum(
                max(0, (min(datetime.combine(datetime.today(), r.end_time), datetime.combine(datetime.today(), SHIFT_C_END)) - 
                          max(datetime.combine(datetime.today(), r.start_time), datetime.combine(datetime.today(), SHIFT_C_START))).total_seconds() // 3600)
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
        assigned_employees_A = assigned_employees_A[::-1]
        assigned_employees_B = assigned_employees_B[::-1]


        # シフトの長さを計算
        shift_lengths = {
            'A': (SHIFT_A_END.hour - SHIFT_A_START.hour),
            'B': (SHIFT_B_END.hour - SHIFT_B_START.hour)
        }

        # シフトの長さでソート
        sorted_shifts = sorted(shift_lengths.items(), key=lambda x: x[1])
        logger.info(f"これだ！！！！{assigned_shifts_A[0]['employee_name']}開始{assigned_shifts_A[0]['shift_start']}と　終了{assigned_shifts_A[0]['shift_end']}")

        # A枠とB枠が割り当てられたかどうかを示すフラグ
        a_assigned = False
        b_assigned = False

        for shift_type, _ in sorted_shifts:
            if shift_type == 'A':
                if (len(assigned_shifts_A) > 1 and
                    assigned_shifts_A[0]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_A[0]['requested_end'] >= SHIFT_C_END and
                    assigned_shifts_A[1]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_A[1]['requested_end'] >= SHIFT_C_END and 
                    SHIFT_A_END.hour - SHIFT_C_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_C_END.hour - SHIFT_A_START.hour <= MAX_SHIFT_HOURS and 
                    (SHIFT_C_START <= assigned_shifts_A[0]['shift_end'] <= SHIFT_C_END or
                     SHIFT_C_START <= assigned_shifts_A[1]['shift_end'] <= SHIFT_C_END)):
                    
                    employee_shift_limits[assigned_employees_A[0].id] += 1
                    employee_shift_limits[assigned_employees_A[1].id] += 1
                    assigned_employees_C = assign_shifts('C', assigned_shifts_A, 'repeat', SHIFT_C_START, SHIFT_C_END, current_date, assigned_employees_A.copy(), db, shifts, employee_shift_limits)
                    employee_shift_limits[assigned_employees_A[0].id] -= 1
                    employee_shift_limits[assigned_employees_A[1].id] -= 1

                    logger.info(f"A枠を被らせました。{assigned_shifts_A[0]['employee_name']}と{assigned_shifts_A[1]['employee_name']}を被らせます")
                    a_assigned = True  # A枠が割り当てられたフラグを立てる
                    break  # A枠が割り当てられた場合はループを終了

            elif shift_type == 'B':
                if (len(assigned_shifts_B) > 1 and
                    assigned_shifts_B[0]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_B[0]['requested_end'] >= SHIFT_C_START and 
                    assigned_shifts_B[1]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_B[1]['requested_end'] >= SHIFT_C_END and 
                    SHIFT_B_END.hour - SHIFT_C_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_C_END.hour - SHIFT_B_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_C_START <= assigned_shifts_B[0]['shift_end'] <= SHIFT_C_END):

                    employee_shift_limits[assigned_employees_B[0].id] += 1
                    employee_shift_limits[assigned_employees_B[1].id] += 1
                    assigned_employees_C = assign_shifts('C', assigned_shifts_B, 'repeat', SHIFT_C_START, SHIFT_C_END, current_date, assigned_employees_B.copy(), db, shifts, employee_shift_limits)
                    employee_shift_limits[assigned_employees_B[0].id] -= 1
                    employee_shift_limits[assigned_employees_B[1].id] -= 1

                    logger.info(f"B枠を被らせました。{assigned_shifts_B[0]['employee_name']}と{assigned_shifts_B[1]['employee_name']}を被らせます")
                    b_assigned = True  # B枠が割り当てられたフラグを立てる
                    break  # B枠が割り当てられた場合はループを終了

        # A枠またはB枠が割り当てられなかった場合の処理
        if not a_assigned and not b_assigned:
            logger.info("被らすのは無理でした。")
            if available_employees_C:
                logger.info(f"Date: {current_date} - Available employees for C shift: {[e.name for e in available_employees_C]}")
                assigned_employees_C = assign_shifts('C', [], 'new', SHIFT_C_START, SHIFT_C_END, current_date, available_employees_C, db, shifts, employee_shift_limits)
                update_remaining_requests(assigned_employees_C, remaining_shift_requests)
            else:
                logger.info(f"Date: {current_date} - No available employees for C shift")
                assigned_employees_C = []

        
        assigned_shifts_C = []

        for employee in assigned_employees_C:
            # 各従業員のシフトリクエストを取得
            request = next((r for r in employee.shift_requests if r.date == current_date), None)
            
            # 実際に割り当てられたシフトの開始時間と終了時間を取得
            assigned_shift = next((s for s in shifts if s.employee_id == employee.id and s.date == current_date), None)
            
            if assigned_shift:
                assigned_shifts_C.append({
                    'employee_name': employee.name,
                    'shift_start': assigned_shift.start_time,  # 実際の開始時間
                    'shift_end': assigned_shift.end_time,      # 実際の終了時間
                    'requested_start': request.start_time if request else None,  # シフト希望開始時間
                    'requested_end': request.end_time if request else None       # シフト希望終了時間
                })



        sorted_dates.remove(current_date)

def select_date_with_fewest_requests(sorted_dates, employees, employee_shift_limits):
    random.shuffle(sorted_dates) 
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