// Карта логотипов проектов
const projectLogos = {
    "GribLand": "/static/gribland.png",
    "MCSkill": "/static/mcskill.png",
    "StreamCraft": "/static/streamcraft.png",
    "SimpleMinecraft": "/static/simpleminecraft.png",
    "GravityCraft": "/static/gravitycraft.png",
    "VimeWorld": "/static/vimeworld.png",
    "Cristalix": "/static/cristalix.png"
};

// Список серверов для каждого проекта
const servers = {
    "GribLand": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "MCSkill": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "StreamCraft": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "SimpleMinecraft": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "GravityCraft": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "VimeWorld": ["OneBlock", "TechnoMagicRPG", "HiTech"],
    "Cristalix": ["OneBlock", "TechnoMagicRPG"]
};

// Фоны для серверов
const serverBackgrounds = {
    "OneBlock": "/static/oneblock-bg.jpg",
    "TechnoMagicRPG": "/static/technomagic-bg.jpg",
    "HiTech": "/static/hitech-bg.jpg"
};

function selectProject(projectName) {
    document.getElementById("server-title").innerText = `Выберите сервер для ${projectName}`;
    document.getElementById("project-logo-img").src = projectLogos[projectName];
    document.getElementById("server-container").style.display = "block";

    let serverListDiv = document.getElementById("server-list");
    serverListDiv.innerHTML = "";

    servers[projectName].forEach(server => {
        let div = document.createElement("div");
        div.className = "server";
        div.innerText = server;

        if (server === "OneBlock") div.classList.add("oneblock-server");
        else if (server === "TechnoMagicRPG") div.classList.add("technomagic-server");
        else if (server === "HiTech") div.classList.add("hitech-server");

        div.onclick = () => {
            window.location.href = `/server/${projectName}/${server}`;
        };

        serverListDiv.appendChild(div);
    });
}

function changeBackgroundSmoothly(newImageUrl) {
    const img = new Image();
    img.src = newImageUrl;

    img.onload = () => {
        document.body.style.backgroundImage = `url(${newImageUrl})`;
    };
}
