function openMenu() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebar-overlay').classList.add('active');
}

function closeMenu() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('active');
}



// Добавьте обработчик для закрытия по клику на оверлей
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }

    // Закрытие по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
});

// server.js - ИСПРАВЛЕННАЯ ВЕРСИЯ
function showSection(sectionId) {
    console.log('Показать секцию:', sectionId);

    // Скрываем все секции
    const sections = [
        'profile-section',
        'moderators-section',
        'activity-section',
        'online-section',
        'salary-section',
        'table-section'
    ];

    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.style.display = 'none';
            console.log('Скрыта секция:', section);
        }
    });

    // Показываем целевую секцию
    const target = document.getElementById(sectionId);
    if (target) {
        target.style.display = 'block';
        console.log('Показана секция:', sectionId);

        // Загружаем данные для конкретных секций
        switch(sectionId) {
            case 'moderators-section':
                if (typeof loadModerators === 'function') loadModerators();
                break;
            case 'table-section':
                if (typeof showTableSection === 'function') showTableSection();
                break;
            case 'salary-section':
                if (typeof showSalaryCalculator === 'function') showSalaryCalculator();
                break;
            case 'activity-section':
                if (typeof loadModeratorActivity === 'function') loadModeratorActivity();
                break;
        }
    } else {
        console.error('Секция не найдена:', sectionId);
    }
}

function hideAllSections() {
    const sections = [
        'profile-section',
        'moderators-section',
        'activity-section',
        'online-section',
        'salary-section',
        'table-section'
    ];

    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.style.display = 'none';
        }
    });
}

// Дополнительные вспомогательные функции
function getProjectName() {
    return document.querySelector('meta[name="project-name"]')?.getAttribute('content') || "GribLand";
}

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

    return `${year}-${month}`;
}

// Универсальная функция для показа уведомлений
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
        transition: opacity 0.5s;
    `;
    notification.textContent = message;

    notificationContainer.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, duration);
}

// Функция для обработки ошибок fetch запросов
async function handleFetchResponse(response) {
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully');

    // Проверяем наличие всех необходимых секций
    const requiredSections = [
        'profile-section',
        'moderators-section',
        'activity-section',
        'online-section',
        'salary-section',
        'table-section'
    ];

    requiredSections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (!section) {
            console.warn(`Section not found: ${sectionId}`);
        }
    });

    // Показываем профиль по умолчанию
    showSection('profile-section');
});