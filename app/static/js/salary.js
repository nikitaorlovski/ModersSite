// === ОБЩИЕ ПЕРЕМЕННЫЕ (выносим в самое начало) ===
const projectName = document.querySelector('meta[name="project-name"]')?.getAttribute('content') || "GribLand";
const serverName = getServerName();

// === УТИЛИТЫ ===
function getServerName() {
    const serverBanner = document.querySelector('.server-banner .sb-value');
    return serverBanner ? serverBanner.textContent.trim() : "OneBlock";
}

function getCurrentMonth(period = 'current') {
    const date = new Date();
    let month, year;

    if (period === 'current') {
        month = (date.getMonth() + 1).toString().padStart(2, '0');
        year = date.getFullYear();
    } else {
        month = (date.getMonth() === 0 ? 12 : date.getMonth()).toString().padStart(2, '0');
        year = date.getMonth() === 0 ? date.getFullYear() - 1 : date.getFullYear();
    }

    return { month, year, monthStr: `${year}-${month}` };
}

function clearTableFields() {
    document.getElementById('questions').value = '';
    document.getElementById('complaints').value = '';
    document.getElementById('severe_complaints').value = '';
    document.getElementById('attached_moderators').value = '';
    document.getElementById('interviews').value = '';
    document.getElementById('online_top').value = '';
    document.getElementById('questions_top').value = '';
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

function showNotification(message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 500);
    }, duration);
}

// === ОСНОВНЫЕ ФУНКЦИИ ===
async function showSalaryCalculator() {
    hideAllSections();
    let salaryContainer = document.getElementById("salary-section");
    let staffList = document.getElementById("staff-list");
    salaryContainer.style.display = "block";

    staffList.innerHTML = `
        <div class="staff-card" style="grid-column: 1 / -1; text-align: center; justify-content: center;">
            <div class="staff-name">Загрузка модераторов...</div>
        </div>
    `;

    try {
        const res = await fetch("/get_staff");
        
        if (!res.ok) throw new Error("Ошибка на сервере");

        const data = await res.json();

        staffList.innerHTML = "";

        const sortedModerators = Object.entries(data.body.users).sort((a, b) => {
            const roleOrder = {
                'group.curator': 1, 'group.grandmoderator': 2, 'group.stmoderator': 3,
                'group.moder': 4, 'group.helper': 5, 'group.stajer': 6
            };
            return roleOrder[a[1]] - roleOrder[b[1]];
        });

        for (const [name, role] of sortedModerators) {
            const roleText = {
                'group.curator': 'Куратор', 'group.grandmoderator': 'Гл.модератор',
                'group.stmoderator': 'Ст.модератор', 'group.moder': 'Модератор',
                'group.helper': 'Хелпер', 'group.stajer': 'Стажёр'
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
        const { month, year } = getCurrentMonth(selectedMonth);

        const startDate = `${year}-${month}-01`;
        const endDate = new Date(year, month, 0).toISOString().split('T')[0];

        const response = await fetch(`/check_online?nickname=${encodeURIComponent(nickname)}&start_date=${startDate}&end_date=${endDate}`);

        if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

        const data = await response.json();
        const onlineHoursInput = document.getElementById('online_hours');

        if (data && data.time) {
            const hoursMatch = data.time.match(/(\d+)ч/);
            const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
            onlineHoursInput.value = hours;
        } else {
            onlineHoursInput.value = 0;
        }
    } catch (error) {
        document.getElementById('online_hours').value = 0;
    }
}

async function loadSavedTableData(nickname) {
    try {
        const monthSelect = document.getElementById('salary-month');
        const selectedMonth = monthSelect.value;
        const { monthStr } = getCurrentMonth(selectedMonth);

        const response = await fetch(`/get_table_data?project=${encodeURIComponent(projectName)}&server=${encodeURIComponent(serverName)}&month=${encodeURIComponent(monthStr)}`);

        if (response.ok) {
            const allData = await response.json();

            const userData = allData.find(item => item.nickname === nickname);

            if (userData) {
                document.getElementById('questions').value = userData.questions || '';
                document.getElementById('complaints').value = userData.complaints || '';
                document.getElementById('severe_complaints').value = userData.severe_complaints || '';
                document.getElementById('attached_moderators').value = userData.attached_moderators || '';
                document.getElementById('interviews').value = userData.interviews || '';
                document.getElementById('online_top').value = userData.online_top || '';
                document.getElementById('questions_top').value = userData.questions_top || '';
            } else {
                clearTableFields();
            }
        } else {
            clearTableFields();
        }
    } catch (error) {
        clearTableFields();
    }
}

async function openSalaryModal(nickname, role) {
    const modal = document.getElementById('salary-modal');
    const staffName = document.getElementById('modal-staff-name');
    const staffRole = document.getElementById('modal-staff-role');
    const staffSkin = document.getElementById('modal-staff-skin');
    const nicknameInput = document.getElementById('nickname');

    staffName.textContent = nickname;
    staffRole.textContent = role;
    staffSkin.src = `https://meta-api.metalabs.work/api/v3/users/skins/${projectName}/head/${nickname}`;
    nicknameInput.value = nickname;

    const severeComplaintsGroup = document.getElementById('severe_complaints_group');
    const interviewsGroup = document.getElementById('interviews_group');

    if (['Куратор', 'Гл.модератор', 'Ст.модератор'].includes(role)) {
        severeComplaintsGroup.style.display = 'block';
        interviewsGroup.style.display = 'block';
    } else {
        severeComplaintsGroup.style.display = 'none';
        interviewsGroup.style.display = 'none';
        document.getElementById('severe_complaints').value = '';
        document.getElementById('interviews').value = '';
    }

    clearSalaryForm();
    await updateOnlineHours(nickname);
    await loadSavedTableData(nickname);
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
        new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().slice(0, 7);

    let report = `💰 Расчет зарплаты для ${role} ${nickname} 💰\n\n`;

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

    window.currentSalaryData = {
        nickname, role, online_hours, questions, complaints, severe_complaints,
        attached_moderators, interviews, online_top, questions_top, gma_review,
        total_salary: Math.round(total_salary), month: selectedMonth
    };

    const salaryResult = document.getElementById('salary-result');
    salaryResult.innerHTML = report;
    salaryResult.style.display = 'block';
    document.getElementById('confirm-salary').style.display = 'inline-block';
}

async function confirmSalary() {
    try {
        if (!window.currentSalaryData) throw new Error('Нет данных для сохранения');

        const role = document.getElementById('modal-staff-role').textContent.trim();
        const status = (role === 'ПСЖ') ? 'ПСЖ' : 'Актив';

        const salaryData = {
            ...window.currentSalaryData,
            project: projectName,
            server: serverName,
            status: status
        };

        const response = await fetch('/save_salary', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
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
    const { monthStr } = getCurrentMonth(selectedMonth);
    const role = window.currentSalaryData.role || 'Модератор';

    try {
        const response = await fetch(`/send_salary_telegram`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ...window.currentSalaryData,
                nickname: nickname,
                role: role,
                month: monthStr,
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
        showNotification('Ошибка при отправке: ' + error.message);
    }
}

async function sendSalaryReportToTelegram() {
    const monthSelect = document.getElementById('report-month');
    const selectedMonth = monthSelect.value;
    const { monthStr } = getCurrentMonth(selectedMonth);

    try {
        const response = await fetch("/send_full_salary_report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project: projectName, server: serverName, month: monthStr })
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

// === ИНИЦИАЛИЗАЦИЯ ===
document.addEventListener('DOMContentLoaded', function() {
    const monthSelect = document.getElementById('salary-month');
    if (monthSelect) {
        monthSelect.addEventListener('change', function() {
            const nickname = document.getElementById('nickname').value;
            if (nickname) {
                updateOnlineHours(nickname);
                loadSavedTableData(nickname);
            }
        });
    }
});