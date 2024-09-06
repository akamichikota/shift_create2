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
MAX_SHIFT_HOURS = 6  # 最高シフト時間

SHIFT_A_START = time(15, 0)  # Aシフトの開始時間
SHIFT_A_END = time(23, 0)    # Aシフトの終了時間
SHIFT_B_START = time(15, 0)  # Bシフトの開始時間
SHIFT_B_END = time(23, 0)    # Bシフトの終了時間
SHIFT_C_START = time(17, 0)  # Cシフトの開始時間
SHIFT_C_END = time(22, 0)    # Cシフトの終了時間
SHIFT_D_START = time(18, 0)  # Dシフトの開始時間
SHIFT_D_END = time(21, 0)    # Dシフトの終了時間

JUNIOR_AVAILABLE_SHIFT_START = time(16, 0)  # 初級者シフトの可能な開始時間
JUNIOR_AVAILABLE_SHIFT_END = time(21, 0)    # 初級者シフトの可能な終了時間

def assign_shifts(shift_type, assigned_shifts, employee_state, shift_start_time, shift_end_time, current_date, available_employees, db, shifts, employee_shift_limits):
    current_shift_start = shift_start_time
    current_shift_end = shift_end_time
    # shift_start_timeをdatetime.datetime型に変換
    shift_start_datetime = datetime.combine(current_date, shift_start_time)
    shift_end_datetime = datetime.combine(current_date, shift_end_time)

    branch_handle_shift_request = 0
    assigned_employees = []

    current_shift_employees = []
    for shift in shifts:
        if shift.date == current_date and shift.employee_id is not None:
            employee = db.query(Employee).filter(Employee.id == shift.employee_id).first()  # Employeeを取得
            if employee:
                shift_info = {
                    'name': employee.name,
                    'rank': employee.rank,
                    'shift_type': shift.shift_type,
                    'start_time': shift.start_time,
                    'end_time': shift.end_time
                }
                current_shift_employees.append(shift_info)

    while current_shift_start != current_shift_end and available_employees:
        employee = available_employees.pop(0) if available_employees else None  # 修正
        if employee is None:  # 修正
            break  # 修正
        request = next((r for r in employee.shift_requests if r.date == current_date), None)
        logger.info(f"Date: {current_date} - Processing employee: {employee.name}, Request: {request}")
        logger.info(f"Date: {current_date} - ランク：{employee.rank}")


        
        # パターン分岐　branch_handle_shift_requestを決定する

        if employee_state == 'new':
            # 上級者を割り当てる際にどの割り当てロジックにとばすか
            if employee.rank == "上級者":
                logger.info(f"Date: {current_date} - {employee.name} 上級者")
                upper_available_shift_start_time = max(request.start_time, shift_start_time)
                upper_available_shift_end_time = min(request.end_time, shift_end_time)
                # 一回目の割り当て時のみペア割り当ての可能性あり
                if shift_start_time == current_shift_start and shift_end_time == current_shift_end:
                    # 前半でも後半でもシフトに入れる状態の上級者
                    if request.start_time <= shift_start_time and request.end_time >= shift_end_time:

                        if any(e.rank == "初級者" for e in available_employees[:5]):
                            # 初級者ランクの従業員を取得
                            junior_employees = [e for e in available_employees[:5] if e.rank == "初級者"]
                            
                            for junior in junior_employees:
                                # シフト希望を取得
                                junior_shift_request = next((r for r in junior.shift_requests if r.date == current_date), None)
                                if junior_shift_request:


                                    junior_request_shift_start_time = junior_shift_request.start_time
                                    junior_request_shift_end_time = junior_shift_request.end_time

                                    junior_available_shift_start_time = max(junior_request_shift_start_time, JUNIOR_AVAILABLE_SHIFT_START)
                                    junior_available_shift_end_time = min(junior_request_shift_end_time, JUNIOR_AVAILABLE_SHIFT_END)

                                    overlap_start_datetime = datetime.combine(current_date, max(junior_available_shift_start_time, upper_available_shift_start_time))
                                    overlap_end_datetime = datetime.combine(current_date, min(junior_available_shift_end_time, upper_available_shift_end_time))


                                    # 前半部分に配置するのか後半部分に配置するのかを決めた後、padding_hoursを計算する。共通時間全てじゃなく、最低時間ぶんを割り当てた時の逆側の余白時間。
                                    if overlap_start_datetime - shift_start_datetime <= shift_end_datetime - overlap_end_datetime:
                                        pair_time_period = 'first'
                                        padding_hours = (shift_end_datetime - (overlap_start_datetime + timedelta(hours=MIN_SHIFT_HOURS))).total_seconds() / 3600
                                        logger.info(f"Date: {current_date} - pair_time_period: {pair_time_period}")
                                        logger.info(f"Date: {current_date} - padding_hours: {padding_hours}")
                                    else:
                                        pair_time_period = 'second'
                                        padding_hours = ((overlap_end_datetime - timedelta(hours=MIN_SHIFT_HOURS)) - shift_start_datetime).total_seconds() / 3600
                                        logger.info(f"Date: {current_date} - pair_time_period: {pair_time_period}")
                                        logger.info(f"Date: {current_date} - padding_hours: {padding_hours}")

                                    # かぶっている時間が最低時間以上で、逆側の余白もちゃんと最低時間以上あるかを確認
                                    if (overlap_end_datetime - overlap_start_datetime >= timedelta(hours=MIN_SHIFT_HOURS) and 
                                        padding_hours >= MIN_SHIFT_HOURS):
                                        logger.info(f"注目！！！！")
                                        logger.info(f"注目！！！！")
                                        logger.info(f"Date: {current_date} - ペアシフト割り当てを適用")
                                        logger.info(f"Date: {current_date} - pair_time_period: {pair_time_period}")
                                        logger.info(f"Date: {current_date} - padding_hours: {padding_hours}")
                                        logger.info(f"注目！！！！")
                                        logger.info(f"注目！！！！")
                                        branch_handle_shift_request = 3
                                        break
                                    else:
                                        logger.info(f"注目！！！！")
                                        logger.info(f"注目！！！！")
                                        logger.info(f"Date: {current_date} - ペアシフト割り当てを適用しない")
                                        logger.info(f"Date: {current_date} - pair_time_period: {pair_time_period}")
                                        logger.info(f"Date: {current_date} - padding_hours: {padding_hours}")
                                        logger.info(f"注目！！！！")
                                        logger.info(f"注目！！！！")
                                        continue
                            
                            if branch_handle_shift_request == 0:
                                branch_handle_shift_request = 1
                            
                        else:
                            branch_handle_shift_request = 1
                else:
                    branch_handle_shift_request = 1



            # 初級者を割り当てる際にどの割り当てロジックにとばすか
            elif employee.rank == "初級者":
                logger.info(f"Date: {current_date} - {employee.name} 初級者")
                junior_available_shift_start_time = max(request.start_time, JUNIOR_AVAILABLE_SHIFT_START)
                junior_available_shift_end_time = min(request.end_time, JUNIOR_AVAILABLE_SHIFT_END)
                # request.start_time と request.end_time を datetime.datetime 型に変換
                request_start_datetime = datetime.combine(current_date, request.start_time)
                request_end_datetime = datetime.combine(current_date, request.end_time)


                if any(emp['rank'] == "上級者" for emp in current_shift_employees):
                    upper_employees = [e for e in current_shift_employees if e['rank'] == "上級者"]
                    logger.info(f"upper_employees: {upper_employees}")

                    for upper_employee in upper_employees:
                        # 今の枠に自分だけ入って尚且つ上級者とペアになれる場合
                        # if (request_start_datetime <= shift_start_datetime and 
                        #     request_end_datetime >= shift_end_datetime and 
                        #     junior_available_shift_start_time <= shift_start_time and
                        #     junior_available_shift_end_time >= shift_end_time and
                        #     (shift_end_datetime - shift_start_datetime).total_seconds() / 3600 >= MIN_SHIFT_HOURS):
                        #     overlap_start_datetime = datetime.combine(current_date, max(shift_start_time, junior_available_shift_start_time, upper_employee['start_time']))
                        #     overlap_end_datetime = datetime.combine(current_date, min(shift_end_time, junior_available_shift_end_time, upper_employee['end_time']))
                        
                        # else:
                        upper_employee_shift_start_time = upper_employee['start_time']
                        upper_employee_shift_end_time = upper_employee['end_time']
                        overlap_start_datetime = datetime.combine(current_date, max(shift_start_time, junior_available_shift_start_time, upper_employee_shift_start_time))
                        overlap_end_datetime = datetime.combine(current_date, min(shift_end_time, junior_available_shift_end_time, upper_employee_shift_end_time))

                        if overlap_end_datetime - overlap_start_datetime >= timedelta(hours=MIN_SHIFT_HOURS):
                            

                            logger.info(f"overlap_start_datetime: {overlap_start_datetime}")
                            logger.info(f"overlap_end_datetime: {overlap_end_datetime}")
                            logger.info(f"Date: {current_date} - 初心者でシフトに入れます。ありがとう！！")
                            branch_handle_shift_request = 2
                            break
                        else:
                            continue
                    
                    if branch_handle_shift_request == 0:
                        logger.info(f"Date: {current_date} - 割り当て済み従業員に上級者がいるけど時間が被っていないため")
                        logger.info(f"Date: {current_date} - {employee.name} はシフトに入れない初級者です。")
                        branch_handle_shift_request = 10

                else:
                    logger.info(f"Date: {current_date} - 今日の割り当て済み従業員に上級者がいないため")
                    logger.info(f"Date: {current_date} - {employee.name} はシフトに入れない初級者です。")
                    branch_handle_shift_request = 10



            # 中級者を割り当てる際にどの割り当てロジックにとばすか
            elif employee.rank == "中級者":
                logger.info(f"Date: {current_date} - {employee.name} 中級者")
                branch_handle_shift_request = 1
            else:
                logger.info(f"エラーかもしれない！！！")
                logger.info(f"エラーかもしれない！！！")
                logger.info(f"エラーかもしれない！！！")

        elif employee_state == 'repeat':
            logger.info(f"Date: {current_date} - {employee.name} 繰り返し")
            branch_handle_shift_request = 1







        # ブランチごとに呼び出す関数を指定

        # デフォルト
        if branch_handle_shift_request == 0:
            logger.info(f"注目！！！！")
            logger.info(f"注目！！！！")
            logger.info(f"Date: {current_date} - デフォルトになった{employee.name} branch_handle_shift_request == 0")
            logger.info(f"注目！！！！")
            logger.info(f"注目！！！！")
            current_shift_start, current_shift_end, assigned_employees = simple_handle_shift_request(
                employee, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
        
        # 中級者と、初級者と関係ない上級者
        elif branch_handle_shift_request == 1:
            logger.info(f"元からあるシンプルなやつでやります。branch_handle_shift_request == 1でした。{employee.name}")
            logger.info(f"Date: {current_date} - 従業員のランク: {employee.rank}")
            current_shift_start, current_shift_end, assigned_employees = simple_handle_shift_request(
                employee, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
        
        # 初級者
        elif branch_handle_shift_request == 2:
            logger.info(f"Date: 初級者にペアシフト割り当てを適用：{employee.name}")
            current_shift_start, current_shift_end, assigned_employees = beginner_handle_shift_request(
                employee, upper_employee_shift_start_time, upper_employee_shift_end_time, junior_available_shift_start_time, junior_available_shift_end_time, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            ) 

        # 上級者(ペア割り当てを実行したやつ)
        elif branch_handle_shift_request == 3:
            logger.info(f"Date: 上級者にペアシフト割り当てを適用：{employee.name}")
            current_shift_start, current_shift_end, assigned_employees = upper_handle_shift_request(
                employee, pair_time_period, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
        
        # 初級者(ペアが見つからなかった)
        elif branch_handle_shift_request == 10:
            logger.info(f"この従業員は破棄しました。：{employee.name}")
            logger.info(f"この従業員は破棄しました。：{employee.name}")
            logger.info(f"この従業員は破棄しました。：{employee.name}")
        
        # その他
        else:
            logger.info(f"エラーかもしれない！！！")
            logger.info(f"エラーかもしれない！！！")
            logger.info(f"エラーかもしれない！！！")



    # 今の枠が完全に埋まっていない時に、その分をデフォルト従業員で埋める
    if current_shift_start < current_shift_end:
        new_shift = create_shift_default(db, current_date, current_shift_start, current_shift_end, shift_type)
        if new_shift:
            shifts.append(new_shift)
            db.add(new_shift)

    logger.info(f"Date: {current_date} - Assigned employees for {shift_type} shift: {[e.name for e in assigned_employees]}")
    return assigned_employees




def simple_handle_shift_request(employee, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    if request:
        if (request.start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or request.end_time >= current_shift_end) and 
            employee_state == 'new' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_start: {current_shift_start}")
            current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_start: {current_shift_start}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

        elif (request.end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or request.start_time <= current_shift_start) and 
            employee_state == 'new' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_end: {current_shift_end}")
            current_shift_end = (datetime.combine(current_date, current_shift_end) - timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_end: {current_shift_end}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

        elif (request.start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or request.end_time >= current_shift_end) and 
            employee_state == 'repeat' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=1)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=1))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_start: {current_shift_start}")
            current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_start: {current_shift_start}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")
        
        elif (request.end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or request.start_time <= current_shift_start) and 
            employee_state == 'repeat' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, request.start_time) >= timedelta(hours=1)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=1))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_end: {current_shift_end}")
            current_shift_end = (datetime.combine(current_date, current_shift_start) - timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_end: {current_shift_end}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

    return current_shift_start, current_shift_end, assigned_employees

def beginner_handle_shift_request(employee, upper_employee_shift_start_time, upper_employee_shift_end_time, junior_available_shift_start_time, junior_available_shift_end_time, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    upper_employee_shift_end_datetime = datetime.combine(current_date, upper_employee_shift_end_time)
    junior_available_shift_start_datetime = datetime.combine(current_date, junior_available_shift_start_time)
    if request:
        if (junior_available_shift_start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or junior_available_shift_end_time >= current_shift_end) and 
            employee_state == 'new' and
            # 大前提はオッケー。可能性はある。
            (datetime.combine(current_date, junior_available_shift_end_time) - datetime.combine(current_date, junior_available_shift_start_time) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            # 前半から始められる。
            upper_employee_shift_start_time <= current_shift_start and


            upper_employee_shift_end_datetime + timedelta(hours=MIN_SHIFT_HOURS)  and


            # 前半に入れる際に、自分のところは最低時間以上確保できる
            (datetime.combine(current_date, min(current_shift_end, upper_employee_shift_end_time)) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):

            # 前半に入れる際に、後半部分が大丈夫か知りたい

            assigned_employees, shift_hours = beginner_process_shift_request(
                employee, upper_employee_shift_start_time, upper_employee_shift_end_time, junior_available_shift_start_time, junior_available_shift_end_time, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_start: {current_shift_start}")
            current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_start: {current_shift_start}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

        elif (junior_available_shift_end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or junior_available_shift_start_time <= current_shift_start) and 
            employee_state == 'new' and
            (datetime.combine(current_date, junior_available_shift_end_time) - datetime.combine(current_date, junior_available_shift_start_time) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            (datetime.combine(current_date, min(current_shift_end, upper_employee_shift_end_time)) - datetime.combine(current_date, max(current_shift_start, upper_employee_shift_start_time)) >= timedelta(hours=MIN_SHIFT_HOURS))):
            assigned_employees, shift_hours = beginner_process_shift_request(
                employee, upper_employee_shift_start_time, upper_employee_shift_end_time, junior_available_shift_start_time, junior_available_shift_end_time, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_end: {current_shift_end}")
            current_shift_end = (datetime.combine(current_date, current_shift_end) - timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_end: {current_shift_end}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

    return current_shift_start, current_shift_end, assigned_employees

def upper_handle_shift_request(employee, pair_time_period, assigned_shifts, request, employee_state, shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    if request:
        if (request.start_time <= current_shift_start and current_shift_start == shift_start_time and (current_shift_end == shift_end_time or request.end_time >= current_shift_end) and 
            pair_time_period == 'first' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'first', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_start: {current_shift_start}")
            current_shift_start = (datetime.combine(current_date, current_shift_start) + timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_start: {current_shift_start}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

        elif (request.end_time >= current_shift_end and current_shift_end == shift_end_time and (current_shift_start == shift_start_time or request.start_time <= current_shift_start) and 
            pair_time_period == 'second' and
            (datetime.combine(current_date, request.end_time) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS)) and
            (datetime.combine(current_date, current_shift_end) - datetime.combine(current_date, current_shift_start) >= timedelta(hours=MIN_SHIFT_HOURS))):
            assigned_employees, shift_hours = process_shift_request(
                employee, assigned_shifts, employee_state, request, 'second', shift_start_time, shift_end_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees
            )
            logger.info(f"Before update current_shift_end: {current_shift_end}")
            current_shift_end = (datetime.combine(current_date, current_shift_end) - timedelta(hours=shift_hours)).time()
            logger.info(f"After update current_shift_end: {current_shift_end}")
            logger.info(f"Date: {current_date} - shift_hours: {shift_hours}, current_shift_start: {current_shift_start}, current_shift_end: {current_shift_end}")

    return current_shift_start, current_shift_end, assigned_employees



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
            start_time=start_datetime_repeat.time(),
            end_time=end_datetime_repeat.time(),
            shift_type=shift_type
        )
        shifts.append(new_shift)
        db.add(new_shift)
        assigned_employees.append(employee)


        
        logger.info(f"Date: {current_date} - Assigned {employee.name} to {shift_type} shift")

    return assigned_employees, shift_hours

def beginner_process_shift_request(employee, upper_employee_shift_start_time, upper_employee_shift_end_time, junior_available_shift_start_time, junior_available_shift_end_time, assigned_shifts, employee_state, request, time_period, start_shift_time, end_shift_time, current_date, current_shift_start, current_shift_end, shift_type, db, shifts, employee_shift_limits, assigned_employees):
    # request.start_time と request.end_time を datetime.datetime に変換
    request_start_datetime = datetime.combine(current_date, junior_available_shift_start_time)
    request_end_datetime = datetime.combine(current_date, junior_available_shift_end_time)
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
    elif time_period == 'second':
        start_datetime = current_shift_end_datetime - timedelta(hours=shift_hours)


    logger.info(f"Date: {current_date} - Calculated shift hours for {employee.name}: {shift_hours}")
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


        
        logger.info(f"Date: {current_date} - Assigned {employee.name} to {shift_type} shift")

    return assigned_employees, shift_hours



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

    assigned_employees_A = []  # A枠の初期化
    assigned_employees_B = []  # B枠の初期化
    assigned_employees_C = []  # C枠の初期化
    assigned_employees_D = []  # D枠の初期化

    while sorted_dates:
        current_date = select_date_with_fewest_requests(sorted_dates, employees, employee_shift_limits)
        if not current_date:
            break
        
        # A枠の割り当て
        available_employees_A = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests)]

        if len(available_employees_A) > 1:
            random.shuffle(available_employees_A)
        
        available_employees_A.sort(key=lambda e: (
            0 if remaining_shift_requests[e.id] - employee_shift_limits[e.id] <= 1 else 1,
            0 if e.rank == "上級者" else 1,
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
        assigned_employees_A = assigned_employees_A[::-1]
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
            0 if e.rank == "上級者" else 1,
            0 if remaining_shift_requests[e.id] - employee_shift_limits[e.id] <= 1 else 1,
            0 if e.rank == "初級者" else 1,
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
        assigned_employees_B = assigned_employees_B[::-1]
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
            0 if remaining_shift_requests[e.id] - employee_shift_limits[e.id] <= 1 else 1,
            0 if e.rank == "初級者" else 1,
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


        # シフトの長さを計算
        shift_lengths = {
            'A': (SHIFT_A_END.hour - SHIFT_A_START.hour),
            'B': (SHIFT_B_END.hour - SHIFT_B_START.hour)
        }

        # シフトの長さでソート
        sorted_shifts = sorted(shift_lengths.items(), key=lambda x: x[1])

        # A枠とB枠が割り当てられたかどうかを示すフラグ
        a_assigned = False
        b_assigned = False

        for shift_type, _ in sorted_shifts:
            if shift_type == 'A':
                if (len(assigned_shifts_A) >= 2 and
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
                    assigned_employees_C = assigned_employees_C[::-1]
                    employee_shift_limits[assigned_employees_A[0].id] -= 1
                    employee_shift_limits[assigned_employees_A[1].id] -= 1

                    shift_type_C = 'repeat'
                    applied_shift_type_C = 'A'

                    logger.info(f"A枠を被らせました。{assigned_shifts_A[0]['employee_name']}と{assigned_shifts_A[1]['employee_name']}を被らせます")
                    a_assigned = True  # A枠が割り当てられたフラグを立てる
                    break  # A枠が割り当てられた場合はループを終了

            elif shift_type == 'B':
                if (len(assigned_shifts_B) >= 2 and
                    assigned_shifts_B[0]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_B[0]['requested_end'] >= SHIFT_C_START and 
                    assigned_shifts_B[1]['requested_start'] <= SHIFT_C_START and 
                    assigned_shifts_B[1]['requested_end'] >= SHIFT_C_END and 
                    SHIFT_B_END.hour - SHIFT_C_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_C_END.hour - SHIFT_B_START.hour <= MAX_SHIFT_HOURS and 
                    (SHIFT_C_START <= assigned_shifts_B[0]['shift_end'] <= SHIFT_C_END or
                     SHIFT_C_START <= assigned_shifts_B[1]['shift_end'] <= SHIFT_C_END)):

                    employee_shift_limits[assigned_employees_B[0].id] += 1
                    employee_shift_limits[assigned_employees_B[1].id] += 1
                    assigned_employees_C = assign_shifts('C', assigned_shifts_B, 'repeat', SHIFT_C_START, SHIFT_C_END, current_date, assigned_employees_B.copy(), db, shifts, employee_shift_limits)
                    assigned_employees_C = assigned_employees_C[::-1]
                    employee_shift_limits[assigned_employees_B[0].id] -= 1
                    employee_shift_limits[assigned_employees_B[1].id] -= 1

                    shift_type_C = 'repeat'
                    applied_shift_type_C = 'B'

                    logger.info(f"B枠を被らせました。{assigned_shifts_B[0]['employee_name']}と{assigned_shifts_B[1]['employee_name']}を被らせます")
                    b_assigned = True  # B枠が割り当てられたフラグを立てる
                    break  # B枠が割り当てられた場合はループを終了

        # A枠またはB枠が割り当てられなかった場合の処理
        if not a_assigned and not b_assigned:
            logger.info("被らすのは無理でした。")
            if available_employees_C:
                logger.info(f"Date: {current_date} - Available employees for C shift: {[e.name for e in available_employees_C]}")
                assigned_employees_C = assign_shifts('C', [], 'new', SHIFT_C_START, SHIFT_C_END, current_date, available_employees_C, db, shifts, employee_shift_limits)
                assigned_employees_C = assigned_employees_C[::-1]
                shift_type_C = 'new'
                applied_shift_type_C = 'C'
                update_remaining_requests(assigned_employees_C, remaining_shift_requests)
            else:
                logger.info(f"Date: {current_date} - No available employees for C shift")
                new_shift = create_shift_default(db, current_date, SHIFT_C_START, SHIFT_C_END, 'C')
                if new_shift:
                    shifts.append(new_shift)
                    db.add(new_shift)
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
                    'requested_end': request.end_time if request else None,       # シフト希望終了時間
                    'shift_type': shift_type_C,
                    'applied_shift_type': applied_shift_type_C
                })



        # D枠の割り当て
        available_employees_D = [e for e in employees if employee_shift_limits[e.id] > 0 and any(r.date == current_date for r in e.shift_requests) and e not in assigned_employees_A and e not in assigned_employees_B and e not in assigned_employees_C]

        if len(available_employees_D) > 1:
            random.shuffle(available_employees_D)
        
        available_employees_D.sort(key=lambda e: (
            0 if remaining_shift_requests[e.id] - employee_shift_limits[e.id] <= 1 else 1,
            0 if e.rank == "初級者" else 1,
            # シフト希望時間帯との重複時間を計算
            sum(
                max(0, (min(datetime.combine(datetime.today(), r.end_time), datetime.combine(datetime.today(), SHIFT_D_END)) - 
                          max(datetime.combine(datetime.today(), r.start_time), datetime.combine(datetime.today(), SHIFT_D_START))).total_seconds() // 3600)
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

        # シフトの長さを計算
        shift_lengths = {
            'A': (SHIFT_A_END.hour - SHIFT_A_START.hour),
            'B': (SHIFT_B_END.hour - SHIFT_B_START.hour),
            'C': (SHIFT_C_END.hour - SHIFT_C_START.hour)
        }

        # シフトの長さでソート
        sorted_shifts = sorted(shift_lengths.items(), key=lambda x: x[1])

        # A枠とB枠とC枠が割り当てられたかどうかを示すフラグ
        a_assigned = False
        b_assigned = False
        c_assigned = False

        for shift_type, _ in sorted_shifts:
            if shift_type == 'A':
                if (len(assigned_shifts_A) >= 2 and
                    (len(assigned_shifts_C) == 0 or (len(assigned_shifts_C) >= 1 and assigned_shifts_C[0]['applied_shift_type'] != 'A')) and
                    assigned_shifts_A[0]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_A[0]['requested_end'] >= SHIFT_D_END and
                    assigned_shifts_A[1]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_A[1]['requested_end'] >= SHIFT_D_END and 
                    SHIFT_A_END.hour - SHIFT_D_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_D_END.hour - SHIFT_A_START.hour <= MAX_SHIFT_HOURS and 
                    (SHIFT_D_START <= assigned_shifts_A[0]['shift_end'] <= SHIFT_D_END or
                     SHIFT_D_START <= assigned_shifts_A[1]['shift_end'] <= SHIFT_D_END)):
                    
                    
                    
                    employee_shift_limits[assigned_employees_A[0].id] += 1
                    employee_shift_limits[assigned_employees_A[1].id] += 1
                    assigned_employees_D = assign_shifts('D', assigned_shifts_A, 'repeat', SHIFT_D_START, SHIFT_D_END, current_date, assigned_employees_A.copy(), db, shifts, employee_shift_limits)
                    assigned_employees_D = assigned_employees_D[::-1]
                    employee_shift_limits[assigned_employees_A[0].id] -= 1
                    employee_shift_limits[assigned_employees_A[1].id] -= 1

                    shift_type_D = 'repeat'
                    applied_shift_type_D = 'A'

                    logger.info(f"A枠を被らせました。{assigned_shifts_A[0]['employee_name']}と{assigned_shifts_A[1]['employee_name']}を被らせます")
                    a_assigned = True  # A枠が割り当てられたフラグを立てる
                    break  # A枠が割り当てられた場合はループを終了

            elif shift_type == 'B':
                if (len(assigned_shifts_B) >= 2 and
                    (len(assigned_shifts_C) == 0 or (len(assigned_shifts_C) >= 1 and assigned_shifts_C[0]['applied_shift_type'] != 'B')) and
                    assigned_shifts_B[0]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_B[0]['requested_end'] >= SHIFT_D_START and 
                    assigned_shifts_B[1]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_B[1]['requested_end'] >= SHIFT_D_END and 
                    SHIFT_B_END.hour - SHIFT_D_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_D_END.hour - SHIFT_B_START.hour <= MAX_SHIFT_HOURS and 
                    (SHIFT_D_START <= assigned_shifts_B[0]['shift_end'] <= SHIFT_D_END or 
                    SHIFT_D_START <= assigned_shifts_B[1]['shift_end'] <= SHIFT_D_END)):

                    logger.info(f"シフトタイプ：{assigned_shifts_C[0]['shift_type']}, 適用先：{assigned_shifts_C[0]['applied_shift_type']}")

                    employee_shift_limits[assigned_employees_B[0].id] += 1
                    employee_shift_limits[assigned_employees_B[1].id] += 1
                    assigned_employees_D = assign_shifts('D', assigned_shifts_B, 'repeat', SHIFT_D_START, SHIFT_D_END, current_date, assigned_employees_B.copy(), db, shifts, employee_shift_limits)
                    assigned_employees_D = assigned_employees_D[::-1]
                    employee_shift_limits[assigned_employees_B[0].id] -= 1
                    employee_shift_limits[assigned_employees_B[1].id] -= 1

                    shift_type_D = 'repeat'
                    applied_shift_type_D = 'B'

                    logger.info(f"B枠を被らせました。{assigned_shifts_B[0]['employee_name']}と{assigned_shifts_B[1]['employee_name']}を被らせます")
                    b_assigned = True  # B枠が割り当てられたフラグを立てる
                    break  # B枠が割り当てられた場合はループを終了
            
            elif shift_type == 'C':
                if (len(assigned_shifts_C) >= 2 and
                    assigned_shifts_C[0]['shift_type'] == 'new' and 
                    assigned_shifts_C[0]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_C[0]['requested_end'] >= SHIFT_D_END and
                    assigned_shifts_C[1]['requested_start'] <= SHIFT_D_START and 
                    assigned_shifts_C[1]['requested_end'] >= SHIFT_D_END and 
                    SHIFT_C_END.hour - SHIFT_D_START.hour <= MAX_SHIFT_HOURS and 
                    SHIFT_D_END.hour - SHIFT_C_START.hour <= MAX_SHIFT_HOURS and 
                    (SHIFT_D_START <= assigned_shifts_C[0]['shift_end'] <= SHIFT_D_END or
                     SHIFT_D_START <= assigned_shifts_C[1]['shift_end'] <= SHIFT_D_END)):

                    logger.info(f"シフトタイプ：{assigned_shifts_C[0]['shift_type']}, 適用先：{assigned_shifts_C[0]['applied_shift_type']}") 
                    
                    employee_shift_limits[assigned_employees_C[0].id] += 1
                    employee_shift_limits[assigned_employees_C[1].id] += 1
                    assigned_employees_D = assign_shifts('D', assigned_shifts_C, 'repeat', SHIFT_D_START, SHIFT_D_END, current_date, assigned_employees_C.copy(), db, shifts, employee_shift_limits)
                    assigned_employees_D = assigned_employees_D[::-1]
                    employee_shift_limits[assigned_employees_C[0].id] -= 1
                    employee_shift_limits[assigned_employees_C[1].id] -= 1

                    shift_type_D = 'repeat'
                    applied_shift_type_D = 'C'

                    logger.info(f"C枠を被らせました。{assigned_shifts_C[0]['employee_name']}と{assigned_shifts_C[1]['employee_name']}を被らせます")
                    c_assigned = True  # C枠が割り当てられたフラグを立てる
                    break  # C枠が割り当てられた場合はループを終了
                    
        # A枠またはB枠が割り当てられなかった場合の処理
        if not a_assigned and not b_assigned and not c_assigned:
            logger.info("被らすのは無理でした。")
            if available_employees_D:
                logger.info(f"Date: {current_date} - Available employees for D shift: {[e.name for e in available_employees_D]}")
                assigned_employees_D = assign_shifts('D', [], 'new', SHIFT_D_START, SHIFT_D_END, current_date, available_employees_D, db, shifts, employee_shift_limits)
                assigned_employees_D = assigned_employees_D[::-1]
                shift_type_D = 'new'
                applied_shift_type_D = 'D'
                update_remaining_requests(assigned_employees_D, remaining_shift_requests)
            else:
                logger.info(f"Date: {current_date} - No available employees for D shift")
                new_shift = create_shift_default(db, current_date, SHIFT_D_START, SHIFT_D_END, 'D')
                if new_shift:
                    shifts.append(new_shift)
                    db.add(new_shift)                
                assigned_employees_D = []

        
        assigned_shifts_D = []

        for employee in assigned_employees_D:
            # 各従業員のシフトリクエストを取得
            request = next((r for r in employee.shift_requests if r.date == current_date), None)
            
            # 実際に割り当てられたシフトの開始時間と終了時間を取得
            assigned_shift = next((s for s in shifts if s.employee_id == employee.id and s.date == current_date), None)
            
            if assigned_shift:
                assigned_shifts_D.append({
                    'employee_name': employee.name,
                    'shift_start': assigned_shift.start_time,  # 実際の開始時間
                    'shift_end': assigned_shift.end_time,      # 実際の終了時間
                    'requested_start': request.start_time if request else None,  # シフト希望開始時間
                    'requested_end': request.end_time if request else None,       # シフト希望終了時間
                    'shift_type': shift_type_D,
                    'applied_shift_type': applied_shift_type_D
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

def create_shift_default(db, current_date, current_shift_start, current_shift_end, shift_type):
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
        return new_shift  # 新しいシフトを返す

    return None  # シフトが作成されなかった場合は None を返す