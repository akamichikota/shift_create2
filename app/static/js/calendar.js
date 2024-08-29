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

    // シフト期間の開始日と終了日を取得
    const startDate = new Date(shiftPeriod.startDate);
    const endDate = new Date(shiftPeriod.endDate);

    // カレンダーの日付を生成
    let date = new Date(startDate);
    while (date <= endDate) {
        const row = document.createElement('tr');
        for (let i = 0; i < 7; i++) {
            const cell = document.createElement('td');
            if (date.getDay() === i && date <= endDate) {
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