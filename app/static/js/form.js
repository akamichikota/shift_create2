document.addEventListener('DOMContentLoaded', function() {
    // 従業員編集フォームの送信処理
    const editEmployeeForm = document.getElementById('edit-employee-form');
    if (editEmployeeForm) {
        editEmployeeForm.addEventListener('submit', async function(event) {
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
                await updateEmployeeList();
                await updateEmployeeTable();
            } else {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = '従業員情報の更新に失敗しました。';
                messageDiv.style.color = 'red';
            }
        });
    }

    // 従業員登録フォームの送信処理
    const employeeForm = document.getElementById('employee-form');
    if (employeeForm) {
        employeeForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const formData = new FormData(this);
            const data = new URLSearchParams();

            for (const pair of formData) {
                data.append(pair[0], pair[1]);
            }

            try {
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
                    messageDiv.textContent = `従業員の作成に失敗しました。ステータスコード: ${response.status}`;
                    messageDiv.style.color = 'red';
                }
            } catch (error) {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = `従業員の作成中にエラーが発生しました: ${error.message}`;
                messageDiv.style.color = 'red';
            }
        });
    }

    // シフト希望追加フォームの送信処理
    const shiftRequestForm = document.getElementById('shift-request-form');
    if (shiftRequestForm) {
        shiftRequestForm.addEventListener('submit', async function(event) {
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
                await updateEmployeeTable();
                await updateEmployeeList();
            } else {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = 'シフト希望の追加に失敗しました。';
                messageDiv.style.color = 'red';
            }
        });
    }

    // シフト期間設定フォームの送信処理
    const shiftPeriodForm = document.getElementById('shift-period-form');
    if (shiftPeriodForm) {
        shiftPeriodForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log('フォーム送信イベントがキャンセルされました');

            const formData = new FormData(this);
            const data = new URLSearchParams();

            for (const pair of formData) {
                data.append(pair[0], pair[1]);
            }

            try {
                const response = await fetch('/shift/set-shift-period', {
                    method: 'POST',
                    body: data
                });

                if (response.ok) {
                    const result = await response.json();
                    const messageDiv = document.getElementById('message');
                    messageDiv.textContent = 'シフト期間が正常に設定されました！';
                    messageDiv.style.color = 'green';
                    this.reset();
                    // シフト期間の表示を更新
                    await updateEmployeeTable();
                    const currentShiftPeriodDiv = document.getElementById('current-shift-period');
                    currentShiftPeriodDiv.textContent = `開始日: ${result.start_date}, 終了日: ${result.end_date}`;
                } else {
                    const messageDiv = document.getElementById('message');
                    messageDiv.textContent = `シフト期間の設定に失敗しました。ステータスコード: ${response.status}`;
                    messageDiv.style.color = 'red';
                }
            } catch (error) {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = `シフト期間の設定中にエラーが発生しました: ${error.message}`;
                messageDiv.style.color = 'red';
            }
        });
    }
});