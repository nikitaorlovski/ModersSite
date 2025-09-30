// static/js/table.js
let currentTableData = [];

async function showTableSection() {
    console.log('showTableSection вызвана');

    hideAllSections();
    const tableSection = document.getElementById('table-section');

    if (tableSection) {
        tableSection.style.display = 'block';
        console.log('Таблица показана, загружаем данные...');
        await loadTableData();
    } else {
        console.error('Секция table-section не найдена в DOM');
    }
}

async function loadTableData() {
    console.log('loadTableData начал выполнение');

    try {
        const projectName = document.querySelector('meta[name="project-name"]')?.getAttribute('content') || "GribLand";
        const serverBanner = document.querySelector('.server-banner .sb-value');
        const serverName = serverBanner ? serverBanner.textContent.trim() : "OneBlock";

        console.log('Project:', projectName, 'Server:', serverName);

        const monthSelect = document.getElementById('table-month');
        const selectedMonth = monthSelect ? monthSelect.value : 'current';

        const date = new Date();
        let month, year;
        if (selectedMonth === 'current') {
            month = (date.getMonth() + 1).toString().padStart(2, '0');
            year = date.getFullYear();
        } else {
            month = (date.getMonth() === 0 ? 12 : date.getMonth()).toString().padStart(2, '0');
            year = date.getMonth() === 0 ? date.getFullYear() - 1 : date.getFullYear();
        }

        const monthStr = `${year}-${month}`;
        console.log('Месяц:', monthStr);

        // Показываем индикатор загрузки
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px;">🔄 Загрузка данных...</td></tr>';

        // Получаем список модераторов
        console.log('Запрашиваем /get_staff...');
        const staffResponse = await fetch('/get_staff');

        if (!staffResponse.ok) {
            throw new Error(`Ошибка сервера: ${staffResponse.status}`);
        }

        const staffData = await staffResponse.json();
        console.log('Данные модераторов:', staffData);

        if (!staffData.body || !staffData.body.users) {
            throw new Error('Не удалось загрузить список модераторов');
        }

        // Получаем сохраненные данные таблицы
        console.log('Запрашиваем данные таблицы...');
        const tableResponse = await fetch(`/get_table_data?project=${encodeURIComponent(projectName)}&server=${encodeURIComponent(serverName)}&month=${encodeURIComponent(monthStr)}`);

        let savedData = [];
        if (tableResponse.ok) {
            savedData = await tableResponse.json();
            console.log('Сохраненные данные:', savedData);
        } else {
            console.warn('Не удалось загрузить сохраненные данные таблицы');
        }

        // Создаем карту сохраненных данных для быстрого доступа
        const savedDataMap = {};
        savedData.forEach(item => {
            savedDataMap[item.nickname] = item;
        });

        // Сортируем модераторов по ролям
        const moderators = Object.entries(staffData.body.users)
            .sort((a, b) => {
                const roleOrder = {
                    'group.curator': 1,
                    'group.grandmoderator': 2,
                    'group.stmoderator': 3,
                    'group.moder': 4,
                    'group.helper': 5,
                    'group.stajer': 6
                };
                return (roleOrder[a[1]] || 999) - (roleOrder[b[1]] || 999);
            });

        console.log('Отсортированные модераторы:', moderators);

        // Генерируем HTML таблицы
        tbody.innerHTML = '';
        currentTableData = [];

        if (moderators.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px;">👥 Нет данных о модераторах</td></tr>';
            return;
        }

        moderators.forEach(([nickname, roleCode]) => {
            const saved = savedDataMap[nickname] || {};

            const rowData = {
                nickname: nickname,
                project: projectName,
                server: serverName,
                month: monthStr,
                online_hours: saved.online_hours || 0,
                questions: saved.questions || 0,
                complaints: saved.complaints || 0,
                severe_complaints: saved.severe_complaints || 0,
                attached_moderators: saved.attached_moderators || 0,
                interviews: saved.interviews || 0,
                online_top: saved.online_top || '',
                questions_top: saved.questions_top || ''
            };

            currentTableData.push(rowData);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="nickname-cell">${nickname}</td>
                <td><input type="number" value="${rowData.online_hours}" data-field="online_hours" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.questions}" data-field="questions" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.complaints}" data-field="complaints" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.severe_complaints}" data-field="severe_complaints" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.attached_moderators}" data-field="attached_moderators" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.interviews}" data-field="interviews" data-nickname="${nickname}"></td>
                <td><input type="number" value="${rowData.online_top}" data-field="online_top" data-nickname="${nickname}" min="1" max="3" placeholder="-"></td>
                <td><input type="number" value="${rowData.questions_top}" data-field="questions_top" data-nickname="${nickname}" min="1" max="3" placeholder="-"></td>
                <td><button class="save-row-btn" onclick="saveRowData('${nickname}')">💾</button></td>
            `;
            tbody.appendChild(row);
        });

        // Добавляем обработчики изменений
        addInputListeners();
        console.log('Таблица успешно загружена');

    } catch (error) {
        console.error('Ошибка загрузки данных таблицы:', error);
        const tbody = document.getElementById('table-body');
        tbody.innerHTML =
            `<tr><td colspan="10" style="text-align: center; color: #ff4444; padding: 40px;">
                ❌ Ошибка загрузки: ${error.message}
                <br><button onclick="loadTableData()" style="margin-top: 10px; padding: 8px 16px; background: #ff4444; color: white; border: none; border-radius: 6px; cursor: pointer;">Повторить</button>
            </td></tr>`;
    }
}

function addInputListeners() {
    const inputs = document.querySelectorAll('#table-body input');
    inputs.forEach(input => {
        // Удаляем старые обработчики
        input.removeEventListener('input', handleInputChange);
        // Добавляем новые
        input.addEventListener('input', handleInputChange);
    });
}

function handleInputChange(event) {
    const input = event.target;
    const nickname = input.getAttribute('data-nickname');
    const field = input.getAttribute('data-field');
    let value = input.value;

    // Для числовых полей преобразуем в число, для пустых строк оставляем пустым
    if (value === '') {
        value = '';
    } else {
        value = parseInt(value) || 0;
    }

    // Обновляем данные в currentTableData
    const rowData = currentTableData.find(row => row.nickname === nickname);
    if (rowData) {
        rowData[field] = value;
        console.log(`Обновлено: ${nickname}.${field} = ${value}`);
    }
}

async function saveRowData(nickname) {
    console.log('Сохранение строки для:', nickname);

    const rowData = currentTableData.find(row => row.nickname === nickname);
    if (!rowData) {
        showNotification('❌ Данные для сохранения не найдены');
        return;
    }

    try {
        const response = await fetch('/save_table_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rowData)
        });

        if (response.ok) {
            showNotification(`✅ Данные для ${nickname} сохранены`);
        } else {
            const errorText = await response.text();
            throw new Error(errorText || 'Ошибка сервера');
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        showNotification('❌ Ошибка сохранения: ' + error.message);
    }
}

async function saveAllTableData() {
    console.log('Сохранение всех данных...');

    try {
        const response = await fetch('/save_table_data_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentTableData)
        });

        if (response.ok) {
            showNotification('✅ Все данные успешно сохранены');
        } else {
            const errorText = await response.text();
            throw new Error(errorText || 'Ошибка сервера');
        }
    } catch (error) {
        console.error('Ошибка сохранения всех данных:', error);
        showNotification('❌ Ошибка сохранения: ' + error.message);
    }
}

// Простая функция уведомлений (если её нет)
function showNotification(message, duration = 3000) {
    // Создаем или находим контейнер для уведомлений
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
        `;
        document.body.appendChild(notificationContainer);
    }

    const notification = document.createElement('div');
    notification.style.cssText = `
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #FFD700;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    notification.textContent = message;

    notificationContainer.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, duration);
}