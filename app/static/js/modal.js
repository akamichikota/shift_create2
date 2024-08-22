// モーダルを開く
function openShiftRequestModal(employeeId) {
    document.getElementById('modal_employee_id').value = employeeId;
    document.getElementById('shiftRequestModal').style.display = "block";
    resetShiftRequests(); // シフト希望のリセット
    loadCalendar();
}

function openEditEmployeeModal(employeeId, name, weeklyShifts) {
    document.getElementById('edit_employee_id').value = employeeId;
    document.getElementById('edit_employee_name').value = name;
    document.getElementById('edit_weekly_shifts').value = weeklyShifts;
    document.getElementById('editEmployeeModal').style.display = "block";
}

function closeEditEmployeeModal() {
    document.getElementById('editEmployeeModal').style.display = "none";
}

function closeShiftRequestModal() {
    document.getElementById('shiftRequestModal').style.display = "none";
}

function openTimeSelectModal(date) {
    document.getElementById('timeSelectModal').style.display = "block";
    document.getElementById('timeSelectModal').dataset.selectedDate = date;
    resetTimeOptions(); // 時間選択のリセット
    loadTimeOptions();

    // 初期状態で開始時間と終了時間を選択
    const startTimeButton = document.querySelector('#start-time-options button[data-time="17:00"]');
    const endTimeButton = document.querySelector('#end-time-options button[data-time="01:00"]');
    if (startTimeButton) startTimeButton.classList.add('selected');
    if (endTimeButton) endTimeButton.classList.add('selected');
}

function closeTimeSelectModal() {
    document.getElementById('timeSelectModal').style.display = "none";
}