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

document.getElementById('edit-employee-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const employeeId = document.getElementById('edit_employee_id').value;
    const name = document.getElementById('edit_employee_name').value;
    const weeklyShifts = document.getElementById('edit_weekly_shifts').value;

    const response = await fetch(`/employee/edit-employee/${employeeId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, weekly_shifts: weeklyShifts })
    });

    if (response.ok) {
        closeEditEmployeeModal();
        updateEmployeeList();
        updateEmployeeTable();
    } else {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = '従業員情報の更新に失敗しました。';
        messageDiv.style.color = 'red';
    }
});

// シフト希望のリセット
function resetShiftRequests() {
    const selectedDatesContainer = document.getElementById('selected-dates');
    selectedDatesContainer.innerHTML = '';
}

// モーダルを閉じる
function closeShiftRequestModal() {
    document.getElementById('shiftRequestModal').style.display = "none";
}

// 時間選択モーダルを開く
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

// 時間選択のリセット
function resetTimeOptions() {
    document.querySelectorAll('#start-time-options .selected, #end-time-options .selected').forEach(btn => {
        btn.classList.remove('selected');
    });
}

// 時間選択モーダルを閉じる
function closeTimeSelectModal() {
    document.getElementById('timeSelectModal').style.display = "none";
}

// カレンダーを読み込む
function loadCalendar() {
    const calendarContainer = document.getElementById('calendar-container');
    calendarContainer.innerHTML = ''; // 既存のカレンダーをクリア

    const calendar = document.createElement('table');
    calendar.id = 'calendar';

    // カレンダーのヘッダーを生成
    const headerRow = document.createElement('tr');
    const daysOfWeek = ['日', '月', '火', '水', '木', '金', '土'];
    daysOfWeek.forEach(day => {
        const th = document.createElement('th');
        th.textContent = day;
        headerRow.appendChild(th);
    });
    calendar.appendChild(headerRow);

    // カレンダーの日付を生成
    let date = new Date(2024, 7, 1); // 2024年8月1日
    while (date.getMonth() === 7) {
        const row = document.createElement('tr');
        for (let i = 0; i < 7; i++) {
            const cell = document.createElement('td');
            if (date.getMonth() === 7 && date.getDay() === i) {
                const dateButton = document.createElement('button');
                dateButton.textContent = date.getDate();
                const currentDate = formatDate(date); // 現在の日付をキャプチャ
                dateButton.onclick = () => openTimeSelectModal(currentDate);
                cell.appendChild(dateButton);
                date.setDate(date.getDate() + 1);
            } else {
                cell.appendChild(document.createTextNode(''));
            }
            row.appendChild(cell);
        }
        calendar.appendChild(row);
    }

    calendarContainer.appendChild(calendar);
}

// 日付をYYYY-MM-DD形式にフォーマットする関数
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// シフト希望を追加（ローカルに保存）
function addShiftRequest() {
    const date = document.getElementById('timeSelectModal').dataset.selectedDate;
    const startTime = document.querySelector('#start-time-options .selected').dataset.time;
    const endTime = document.querySelector('#end-time-options .selected').dataset.time;

    const selectedDatesContainer = document.getElementById('selected-dates');
    const shiftRequestDiv = document.createElement('div');
    shiftRequestDiv.textContent = `${date} ${startTime} - ${endTime}`;
    shiftRequestDiv.dataset.date = date;
    shiftRequestDiv.dataset.startTime = startTime;
    shiftRequestDiv.dataset.endTime = endTime;

    const deleteButton = document.createElement('button');
    deleteButton.textContent = '削除';
    deleteButton.onclick = () => shiftRequestDiv.remove();
    shiftRequestDiv.appendChild(deleteButton);

    selectedDatesContainer.appendChild(shiftRequestDiv);

    closeTimeSelectModal();
}

// シフト希望追加フォームの送信
document.getElementById('shift-request-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const employeeId = document.getElementById('modal_employee_id').value;
    const selectedDatesContainer = document.getElementById('selected-dates');
    const shiftRequests = [];

    selectedDatesContainer.querySelectorAll('div').forEach(div => {
        shiftRequests.push({
            date: div.dataset.date,
            start_time: div.dataset.startTime,
            end_time: div.dataset.endTime
        });
    });

    const response = await fetch('/shift/add-shift-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            employee_id: employeeId,
            shift_requests: shiftRequests
        })
    });

    if (response.ok) {
        const result = await response.json();
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'シフト希望が正常に追加されました！';
        messageDiv.style.color = 'green';
        this.reset();
        closeShiftRequestModal();
        updateEmployeeTable();
        updateEmployeeList();
    } else {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'シフト希望の追加に失敗しました。';
        messageDiv.style.color = 'red';
    }
});

// シフト希望削除
async function deleteShiftRequest(shiftRequestId) {
    const response = await fetch(`/shift/delete-shift-request/${shiftRequestId}`, {
        method: 'POST'
    });

    if (response.ok) {
        document.getElementById(`shift-request-${shiftRequestId}`).remove();
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'シフト希望が削除されました！';
        messageDiv.style.color = 'green';

        // 従業員情報まとめ表の更新
        updateEmployeeTable();
    } else {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = 'シフト希望の削除に失敗しました。';
        messageDiv.style.color = 'red';
    }
}

// 従業員情報まとめ表の更新
async function updateEmployeeTable() {
    const response = await fetch('/');
    if (response.ok) {
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTable = doc.querySelector('.table-container').innerHTML;
        document.querySelector('.table-container').innerHTML = newTable;
    }
}

// 現在の従業員リストの更新
async function updateEmployeeList() {
    const response = await fetch('/');
    if (response.ok) {
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newList = doc.querySelector('#employee-list').innerHTML;
        document.querySelector('#employee-list').innerHTML = newList;
    }
}

// 従業員削除
async function deleteEmployee(employeeId) {
    if (!confirm("本当に消しますか？")) {
        return;
    }

    const response = await fetch(`/employee/delete-employee/${employeeId}`, {
        method: 'POST'
    });

    if (response.ok) {
        const employeeElement = document.getElementById(`employee-${employeeId}`);
        if (employeeElement) {
            employeeElement.remove();
        }
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = '従業員が削除されました！';
        messageDiv.style.color = 'green';

        // 従業員情報まとめ表の更新
        await updateEmployeeTable();

        // 現在の従業員リストの更新
        await updateEmployeeList();
    } else {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = '従業員の削除に失敗しました。';
        messageDiv.style.color = 'red';
    }
}

// 従業員登録フォームの送信
document.getElementById('employee-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = new URLSearchParams();
    for (const pair of formData) {
        data.append(pair[0], pair[1]);
    }

    const response = await fetch('/employee/create-employee', {
        method: 'POST',
        body: data
    });

    if (response.ok) {
        const result = await response.json();
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = '従業員が正常に作成されました！';
        messageDiv.style.color = 'green';
        this.reset();
        // 新しい従業員をリストに追加
        const employeeList = document.getElementById('employee-list');
        const newEmployee = document.createElement('li');
        newEmployee.id = `employee-${result.id}`;
        newEmployee.innerHTML = `${formData.get('name')} (週${formData.get('weekly_shifts')}シフト望)`;
        newEmployee.innerHTML += `<button onclick="openShiftRequestModal('${result.id}')">シフト希望を追加</button><button class="delete-button" onclick="deleteEmployee('${result.id}')">削除</button><ul></ul>`;
        employeeList.appendChild(newEmployee);

        // 従業員情報まとめ表の更新
        await updateEmployeeTable();

        // 現在の従業員リストの更新
        await updateEmployeeList();
    } else {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = '従業員の作成に失敗しました。';
        messageDiv.style.color = 'red';
    }
});

// 時間候補を読み込む
function loadTimeOptions() {
    const startTimeOptions = document.getElementById('start-time-options');
    const endTimeOptions = document.getElementById('end-time-options');
    startTimeOptions.innerHTML = '';
    endTimeOptions.innerHTML = '';

    const times = ['17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00'];

    times.forEach(time => {
        const startTimeOption = document.createElement('button');
        startTimeOption.textContent = time;
        startTimeOption.dataset.time = time;
        startTimeOption.onclick = () => selectTimeOption(startTimeOption, 'start');
        startTimeOptions.appendChild(startTimeOption);

        const endTimeOption = document.createElement('button');
        endTimeOption.textContent = time;
        endTimeOption.dataset.time = time;
        endTimeOption.onclick = () => selectTimeOption(endTimeOption, 'end');
        endTimeOptions.appendChild(endTimeOption);
    });
}

// 時間候補を選択
function selectTimeOption(button, type) {
    const optionsContainer = type === 'start' ? document.getElementById('start-time-options') : document.getElementById('end-time-options');
    optionsContainer.querySelectorAll('button').forEach(btn => btn.classList.remove('selected'));
    button.classList.add('selected');
}