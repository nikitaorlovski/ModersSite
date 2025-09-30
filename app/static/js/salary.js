async function showSalaryCalculator() {
    hideAllSections();
    let salaryContainer = document.getElementById("salary-section");
    let staffList = document.getElementById("staff-list");
    salaryContainer.style.display = "block";

    // Получаем project_name из метатега
    var projectName = document.querySelector('meta[name="project-name"]').getAttribute('content');

    staffList.innerHTML = `
        <div class="staff-card" style="grid-column: 1 / -1; text-align: center; justify-content: center;">
            <div class="staff-name">Загрузка модераторов...</div>
        </div>
    `;

    try {
        console.log("Запрос на /get_staff...");
        const res = await fetch("/get_staff");
        console.log("Ответ от /get_staff:", res);

        if (!res.ok) {
            throw new Error("Ошибка на сервере");
        }

        const data = await res.json();
        console.log("Данные от /get_staff:", data);

        staffList.innerHTML = "";

        // Сортируем модераторов по ролям для красивого отображения
        const sortedModerators = Object.entries(data.body.users).sort((a, b) => {
            const roleOrder = {
                'group.curator': 1,
                'group.grandmoderator': 2,
                'group.stmoderator': 3,
                'group.moder': 4,
                'group.helper': 5,
                'group.stajer': 6
            };
            return roleOrder[a[1]] - roleOrder[b[1]];
        });

        for (const [name, role] of sortedModerators) {
            const roleText = {
                'group.curator': 'Куратор',
                'group.grandmoderator': 'Гл.модератор',
                'group.stmoderator': 'Ст.модератор',
                'group.moder': 'Модератор',
                'group.helper': 'Хелпер',
                'group.stajer': 'Стажёр'
            }[role] || role;

            staffList.innerHTML += `
                <div class="staff-card" onclick="openSalaryModal('${name}','${roleText}')">
                    <img src="https://meta-api.metalabs.work/api/v3/users/skins/${projectName}/head/${name}"
                         class="staff-skin" alt="${name}">
                    <div class="staff-info">
                        <div class="staff-name">${name}</div>
                        <div class="staff-role" data-role="${roleText}">${roleText}</div>
                    </div>
                </div>`;
        }
    } catch (err) {
        console.error("Ошибка загрузки данных:", err);
        staffList.innerHTML = `
            <div class="staff-card" style="grid-column: 1 / -1; text-align: center; justify-content: center; background: rgba(255,0,0,0.1);">
                <div class="staff-name" style="color: #ff4444;">❌ Ошибка загрузки данных</div>
                <div class="staff-role">${err.message}</div>
            </div>
        `;
    }
}

async function updateOnlineHours(nickname) {
    try {
        const monthSelect = document.getElementById('salary-month');
        const selectedMonth = monthSelect.value;

        // Получаем даты для выбранного месяца
        const now = new Date();
        let year = now.getFullYear();
        let month = now.getMonth() + 1; // Текущий месяц (1-12)

        if (selectedMonth === 'previous') {
            month = month - 1;
            if (month === 0) {
                month = 12;
                year = year - 1;
            }
        }

        const startDate = `${year}-${month.toString().padStart(2, '0')}-01`;
        const endDate = new Date(year, month, 0).toISOString().split('T')[0];

        console.log(`🔍 Запрос онлайна для ${nickname} за ${startDate} - ${endDate}`);

        const response = await fetch(`/check_online?nickname=${encodeURIComponent(nickname)}&start_date=${startDate}&end_date=${endDate}`);

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();

        const onlineHoursInput = document.getElementById('online_hours');

        if (data && data.time) {
            // Извлекаем часы из строки "119ч 45м"
            const hoursMatch = data.time.match(/(\d+)ч/);
            const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
            onlineHoursInput.value = hours;
            console.log(`✅ Установлено значение: ${hours} часов`);
        } else {
            onlineHoursInput.value = 0;
        }

    } catch (error) {
        document.getElementById('online_hours').value = 0;
    }
}
// Добавьте этот код после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    const monthSelect = document.getElementById('salary-month');
    if (monthSelect) {
        monthSelect.addEventListener('change', function() {
            const nickname = document.getElementById('nickname').value;
            if (nickname) {
                updateOnlineHours(nickname);
            }
        });
    }
});
function openSalaryModal(nickname, role) {
    const modal = document.getElementById('salary-modal');
    const staffName = document.getElementById('modal-staff-name');
    const staffRole = document.getElementById('modal-staff-role');
    const staffSkin = document.getElementById('modal-staff-skin');
    const nicknameInput = document.getElementById('nickname');

    // Устанавливаем данные
    staffName.textContent = nickname;
    staffRole.textContent = role;

    // Получаем project_name для скина
    const projectName = document.querySelector('meta[name="project-name"]').getAttribute('content');
    staffSkin.src = `https://meta-api.metalabs.work/api/v3/users/skins/${projectName}/head/${nickname}`;

    nicknameInput.value = nickname;

    // Скрываем/показываем поля в зависимости от роли
    const severeComplaintsGroup = document.getElementById('severe_complaints_group');
    const interviewsGroup = document.getElementById('interviews_group');

    if (role === 'Куратор' || role === 'Гл.модератор' || role === 'Ст.модератор') {
        severeComplaintsGroup.style.display = 'block';
        interviewsGroup.style.display = 'block';
    } else {
        severeComplaintsGroup.style.display = 'none';
        interviewsGroup.style.display = 'none';
        // Очищаем значения
        document.getElementById('severe_complaints').value = '';
        document.getElementById('interviews').value = '';
    }

    // Очищаем форму
    clearSalaryForm();

    // Получаем онлайн за выбранный месяц
    updateOnlineHours(nickname);

    // Показываем модальное окно
    modal.classList.add('show');
}

function closeSalaryModal() {
    document.getElementById('salary-modal').classList.remove('show');
}

function calculateStaffSalary() {
    const nickname = document.getElementById('nickname').value;
    const role = document.getElementById('modal-staff-role').textContent;
    const online_hours = parseInt(document.getElementById('online_hours').value) || 0;
    const questions = parseInt(document.getElementById('questions').value) || 0;
    const complaints = parseInt(document.getElementById('complaints').value) || 0;
    const severe_complaints = parseInt(document.getElementById('severe_complaints').value) || 0;
    const attached_moderators = parseInt(document.getElementById('attached_moderators').value) || 0;
    const interviews = parseInt(document.getElementById('interviews').value) || 0;
    const online_top = document.getElementById('online_top').value ? parseInt(document.getElementById('online_top').value) : null;
    const questions_top = document.getElementById('questions_top').value ? parseInt(document.getElementById('questions_top').value) : null;
    const gma_review = parseInt(document.getElementById('gma_review').value) || 0;

    const monthSelect = document.getElementById('salary-month');
    const selectedMonth = monthSelect.value === 'current' ?
        new Date().toISOString().slice(0, 7) :
        (() => {
            const date = new Date();
            date.setMonth(date.getMonth() - 1);
            return date.toISOString().slice(0, 7);
        })();

    let report = `💰 Расчет зарплаты для ${role} ${nickname} 💰\n\n`;

    // Базовые начисления
    const online_payment = online_hours <= 40 ? online_hours * 7 : 40 * 10 + (online_hours - 40) * 12;
    report += `🔹 Онлайн (${online_hours} ч) = ${online_payment} рубинов\n`;
    report += `🔹 Вопрос-ответ (${questions}) = ${questions * 10} рубинов\n`;
    report += `🔹 Жалобы (${complaints}) = ${complaints * 10} рубинов\n`;
    report += `🔹 Жалобы на модераторов (${severe_complaints}) = ${severe_complaints * 15} рубинов\n`;
    report += `🔹 Прикрепленные модераторы (${attached_moderators}) = ${attached_moderators * 100} рубинов\n`;
    report += `🔹 Собеседования (${interviews}) = ${interviews * 100} рубинов\n`;

    let base_salary = online_payment + (questions * 10) + (complaints * 10) +
                     (severe_complaints * 15) + (attached_moderators * 100) + (interviews * 100);
    let total_salary = base_salary;

    // Бонусы за топы
    if (online_top) {
        const bonus = {1: 0.15, 2: 0.10, 3: 0.05}[online_top] || 0;
        const bonus_amount = base_salary * bonus;
        total_salary += bonus_amount;
        report += `🏆 Бонус за топ онлайн (${online_top} место) = ${bonus_amount.toFixed(2)} рубинов\n`;
    }

    if (questions_top) {
        const bonus = {1: 0.15, 2: 0.10, 3: 0.05}[questions_top] || 0;
        const bonus_amount = base_salary * bonus;
        total_salary += bonus_amount;
        report += `🏆 Бонус за топ вопросы (${questions_top} место) = ${bonus_amount.toFixed(2)} рубинов\n`;
    }

    total_salary += gma_review;
    report += `🔹 Рецензия ГМА = ${gma_review} рубинов\n\n`;
    report += `💰 **Итого: ${Math.round(total_salary)} рубинов**`;

    // Сохраняем данные во временное хранилище
    window.currentSalaryData = {
        nickname: nickname,
        role: role,
        online_hours: online_hours,
        questions: questions,
        complaints: complaints,
        severe_complaints: severe_complaints,
        attached_moderators: attached_moderators,
        interviews: interviews,
        online_top: online_top,
        questions_top: questions_top,
        gma_review: gma_review,
        total_salary: Math.round(total_salary),
        month: selectedMonth
    };

    const salaryResult = document.getElementById('salary-result');
    salaryResult.innerHTML = report;
    salaryResult.style.display = 'block';

    // Показываем кнопку сохранения
    document.getElementById('confirm-salary').style.display = 'inline-block';
}

function getMonthData(isPrevious = true) {
    const now = new Date();
    let targetMonth, targetYear;

    if (isPrevious) {
        targetMonth = now.getMonth() === 0 ? 11 : now.getMonth() - 1;
        targetYear = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
    } else {
        targetMonth = now.getMonth();
        targetYear = now.getFullYear();
    }

    return {
        month: targetMonth + 1,
        year: targetYear,
        monthStr: `${targetYear}-${String(targetMonth + 1).padStart(2, '0')}`
    };
}

function clearSalaryForm() {
    const inputs = document.querySelectorAll('.salary-form input');
    inputs.forEach(input => {
        if (input.id !== 'nickname') {
            input.value = '';
        }
    });

    document.getElementById('salary-result').style.display = 'none';
    document.getElementById('confirm-salary').style.display = 'none';
    document.getElementById('send-telegram').style.display = 'none';
}
function getServerName() {
    // Получаем из элемента .server-banner
    const serverBanner = document.querySelector('.server-banner .sb-value');
    if (serverBanner) {
        return serverBanner.textContent.trim();
    }

    // Fallback на случай если элемент не найден
    return "OneBlock"; // или другое значение по умолчанию
}

const projectName = document.querySelector('meta[name="project-name"]')?.getAttribute('content') || "GribLand";
const serverName = getServerName(); // Используем функцию

console.log("Project:", projectName, "Server:", serverName); // для отладки
// === КОНЕЦ ДОБАВЛЕНИЯ ===

// Затем идет ваш существующий код...
async function confirmSalary() {
    try {
        if (!window.currentSalaryData) {
            throw new Error('Нет данных для сохранения');
        }

        const role = document.getElementById('modal-staff-role').textContent.trim();
        const status = (role === 'ПСЖ') ? 'ПСЖ' : 'Актив';

        const salaryData = {
            ...window.currentSalaryData,
            project: projectName, // Теперь переменная доступна
            server: serverName,   // Теперь переменная доступна
            status: status
        };

        console.log("Saving salary data:", salaryData); // для отладки

        const response = await fetch('/save_salary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(salaryData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText);
        }

        showNotification('Зарплата успешно сохранена!');
        document.getElementById('send-telegram').style.display = 'inline-block';
    } catch (error) {
        console.error('Error saving salary:', error);
        showNotification('Ошибка при сохранении: ' + error.message);
    }
}

async function sendToTelegram() {
    const nickname = document.getElementById('nickname').value;
    const monthSelect = document.getElementById('salary-month');
    const selectedMonth = monthSelect.value;

    const role = window.currentSalaryData.role || 'Модератор';

    const date = new Date();
    let month, year;

    if (selectedMonth === 'current') {
        month = (date.getMonth() + 1).toString().padStart(2, '0');
        year = date.getFullYear();
    } else {
        if (date.getMonth() === 0) {
            month = '12';
            year = date.getFullYear() - 1;
        } else {
            month = date.getMonth().toString().padStart(2, '0');
            year = date.getFullYear();
        }
    }

    try {
        const response = await fetch(`/send_salary_telegram`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...window.currentSalaryData,
                nickname: nickname,
                role: role,
                month: `${year}-${month}`,
                project: projectName,
                server: serverName
            })
        });


        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Ошибка сервера');
        }

        const result = await response.json();

        if (result.success) {
            showNotification('Отчет успешно отправлен в Telegram!');
            closeSalaryModal();
            clearSalaryForm();
        } else {
            showNotification('Ошибка при отправке: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка при отправке:', error);
        showNotification('Ошибка при отправке: ' + error.message);
    }
}

async function sendSalaryReportToTelegram() {
    const monthSelect = document.getElementById('report-month');
    const selectedMonth = monthSelect.value;

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

    try {
        const response = await fetch("/send_full_salary_report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                project: projectName,
                server: serverName,
                month: monthStr
            })
        });

        const result = await response.json();
        if (result.success) {
            showNotification("Отчет отправлен в Telegram!");
        } else {
            showNotification("Ошибка при отправке отчета: " + (result.error || "неизвестно"));
        }
    } catch (err) {
        showNotification("Ошибка: " + err.message);
    }
}

function showNotification(message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, duration);
}