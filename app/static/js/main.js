// Parallax эффект для MetaLabs
const title = document.querySelector(".parallax-title");
let mouseX = 0, mouseY = 0, currentX = 0, currentY = 0;

document.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.02;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.02;
});

function animate() {
    currentX += (mouseX - currentX) * 0.1;
    currentY += (mouseY - currentY) * 0.1;
    title.style.transform = `translate(${currentX}px, ${currentY}px)`;
    requestAnimationFrame(animate);
}
animate();

// Случайные фразы
const phrases = [
    "А ты отыграл онлайн?",
    "Ты точно заходил сегодня?",
    "Сколько часов у тебя?",
    "Пора обновить свой рекорд!",
    "P.S Killchik Industry"
];

document.addEventListener("DOMContentLoaded", function () {
    const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
    document.querySelector(".tilted-text").innerText = randomPhrase;
});
