function openMenu() {
    document.getElementById("sidebar").style.left = "0";
}

function closeMenu() {
    document.getElementById("sidebar").style.left = "-250px";
}

function showSection(sectionId) {
  document.querySelectorAll('main > div[id$="-section"]').forEach(div => {
    div.style.display = 'none';
  });

  const target = document.getElementById(sectionId);
  if (target) target.style.display = 'block';

  if (sectionId === 'moderators-section' && typeof loadModerators === 'function') {
    loadModerators();
    document.getElementById("staff-stats").style.display = "block";
  } else {
    document.getElementById("staff-stats").style.display = "none";
  }

  // 👉 Добавляем сюда вызов для зарплатного калькулятора
  if (sectionId === 'salary-section' && typeof showSalaryCalculator === 'function') {
    showSalaryCalculator();
  }
}

function hideAllSections() {
    // Скрытие всех секций
    const sections = document.querySelectorAll('main > div[id$="-section"]');
    sections.forEach(section => section.style.display = 'none');
}
