// シフト希望のリセット
function resetShiftRequests() {
    const selectedDatesContainer = document.getElementById('selected-dates');
    selectedDatesContainer.innerHTML = '';
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