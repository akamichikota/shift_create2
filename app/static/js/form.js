document.addEventListener('DOMContentLoaded', function() {
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
                updateEmployeeList();
                updateEmployeeTable();
            } else {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = '従業員情報の更新に失敗しました。';
                messageDiv.style.color = 'red';
            }
        });
    }

    const employeeForm = document.getElementById('employee-form');
    if (employeeForm) {
        employeeForm.addEventListener('submit', async function(event) {
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
    }

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
                updateEmployeeTable();
                updateEmployeeList();
            } else {
                const messageDiv = document.getElementById('message');
                messageDiv.textContent = 'シフト希望の追加に失敗しました。';
                messageDiv.style.color = 'red';
            }
        });
    }
});