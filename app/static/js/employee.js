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