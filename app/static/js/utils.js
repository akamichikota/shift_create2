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

// 時間選択のリセット
function resetTimeOptions() {
    document.querySelectorAll('#start-time-options .selected, #end-time-options .selected').forEach(btn => {
        btn.classList.remove('selected');
    });
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