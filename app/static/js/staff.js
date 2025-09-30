// static/js/staff.js
async function loadModerators() {
    const stats = document.getElementById("staff-stats");
    const container = document.getElementById("moderators-container");

    if (stats) stats.style.display = "block";
    if (container) container.style.display = "block";

    // Пока загружается
    document.querySelectorAll("#moderators-container .moderator-list, #moderators-container div[id$='-list']")
        .forEach(el => el.innerHTML = "<p style='color: #aaa;'>Загрузка...</p>");

    try {
        let response = await fetch("/get_staff");
        let data = await response.json();

        if (!data || !data.body || !data.body.users) {
            container.innerHTML = "<p style='color:red;'>Ошибка: данные состава пустые</p>";
            return;
        }

        // Группы
        const groups = {
            'group.curator': {title: 'Кураторы', listId: 'curators-list'},
            'group.grandmoderator': {title: 'Гл.модераторы', listId: 'grandmoderators-list'},
            'group.stmoderator': {title: 'Ст.модераторы', listId: 'stmoderators-list'},
            'group.moder': {title: 'Модераторы', listId: 'moderators-list'},
            'group.helper': {title: 'Хелперы', listId: 'helpers-list'},
            'group.stajer': {title: 'Стажеры', listId: 'interns-list'}
        };

        // Очищаем контейнеры
        Object.values(groups).forEach(g => {
            const el = document.getElementById(g.listId);
            if (el) el.innerHTML = "";
        });

        // Счётчики
        let counts = {
            total: 0,
            curators: 0,
            grandmods: 0,
            stmods: 0,
            mods: 0,
            helpers: 0,
            interns: 0
        };

        // Заполняем группы
        for (const [name, role] of Object.entries(data.body.users)) {
            if (groups[role]) {
                const el = document.getElementById(groups[role].listId);
                if (el) {
                    el.innerHTML += `<div class="moderator-card">${name}</div>`;
                }

                // Обновляем статистику
                counts.total++;
                if (role === "group.curator") counts.curators++;
                if (role === "group.grandmoderator") counts.grandmods++;
                if (role === "group.stmoderator") counts.stmods++;
                if (role === "group.moder") counts.mods++;
                if (role === "group.helper") counts.helpers++;
                if (role === "group.stajer") counts.interns++;
            }
        }

        // Заполняем статистику
        stats.querySelector('[data-type="total"]').textContent = counts.total;
        stats.querySelector('[data-type="curators"]').textContent = counts.curators;
        stats.querySelector('[data-type="grandmods"]').textContent = counts.grandmods;
        stats.querySelector('[data-type="stmods"]').textContent = counts.stmods;
        stats.querySelector('[data-type="mods"]').textContent = counts.mods;
        stats.querySelector('[data-type="helpers"]').textContent = counts.helpers;
        stats.querySelector('[data-type="interns"]').textContent = counts.interns;

    } catch (err) {
        container.innerHTML = `<p style="color:red;">Ошибка загрузки: ${err.message}</p>`;
    }
}

// Автозагрузка при клике
document.addEventListener("DOMContentLoaded", () => {
    const menuItem = document.querySelector('[onclick="showSection(\'moderators-section\')"]');
    if (menuItem) {
        menuItem.addEventListener("click", () => {
            loadModerators();
        });
    }
});
