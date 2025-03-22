from fastapi import Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
import httpx
from fastapi import FastAPI, Request, Form
from fastapi import Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import os
from app.db import db

app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")



# Настройка сессий
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="app/templates")

# API URL для получения UUID и скина
PLAYTIME_PERIOD_URL_TEMPLATE = "https://meta-api.metalabs.work/api/v3/playtime/{project}/{server}/list?min={min}&max={max}&uuids[]="
API_PLAYTIME_URL = "https://meta-api.metalabs.work/api/v3/playtime"
STAFF_URL_TEMPLATE = "https://meta-api.metalabs.work/api/v3/users/{project}/{server}/staff"
API_BASE_URL = "https://meta-api.metalabs.work/api/v3/users"
PLAYTIME_URL_TEMPLATE = "https://meta-api.metalabs.work/api/v3/playtime/{project}/{server}/list?uuids[]="


@app.on_event("startup")
async def startup():
    await db.connect()
    await db.create_users_table()
    # 👇 Добавляем пользователей, если их ещё нет
    if not await db.user_exists("killchik"):
        await db.add_user("killchik", "adminы")

    if not await db.user_exists("admin"):
        await db.add_user("admin", "password123")

def require_login(request: Request):
    if not request.session.get("username"):
        return RedirectResponse("/", status_code=303)

# ✅ **Маршрут для страницы входа**
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if await db.verify_user(username, password):
        request.session["username"] = username
        return RedirectResponse(url="/projects", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "error": "Неверный логин или пароль"})
# ✅ **Обработка формы логина**


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# ✅ **Страница выбора проекта**
@app.get("/projects")
async def show_projects(request: Request, _: str = Depends(require_login)):
    return templates.TemplateResponse("projects.html", {"request": request})

# ✅ **Страница выбора проекта (после клика)**
@app.get("/select_project/{project_name}")
async def select_project(request: Request, project_name: str, _: str = Depends(require_login)):
    request.session["project_name"] = project_name
    return templates.TemplateResponse("server_selection.html", {"request": request, "project_name": project_name})

# ✅ **Страница выбора сервера**
@app.get("/server/{server_name}")
async def select_server(request: Request, server_name: str, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    request.session["server_name"] = server_name
    username = request.session.get("username", "Неизвестно")

    # Получаем UUID пользователя
    user_uuid = await get_user_uuid(project_name, username)
    user_skin_url = await get_user_skin(project_name, user_uuid)

    # Получаем онлайн игрока за месяц
    monthly_playtime = await get_monthly_playtime(project_name, server_name, user_uuid)

    return templates.TemplateResponse("server_details.html", {
        "request": request,
        "server_name": server_name,
        "project_name": project_name,
        "user_skin_url": user_skin_url,
        "user_uuid": user_uuid,
        "username": username,
        "monthly_playtime": monthly_playtime  # Передаем онлайн в шаблон
    })


import asyncio

@app.get("/get_moderator_activity")
async def get_moderator_activity(request: Request, _: str = Depends(require_login)):
    """Возвращает активность модераторов за текущий месяц, отсортированную по онлайну"""
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    # 🔹 Получаем состав модераторов
    staff = await get_server_staff(project_name, server_name)
    if not staff:
        return {"error": "Не удалось загрузить состав модераторов"}

    all_uuids = staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]

    # 🔹 Получаем все никнеймы разом
    nicknames = await get_nicknames_by_uuids(all_uuids, project_name)

    # 🔹 Запрашиваем игровое время **одним запросом**
    headers = {"Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"}
    url = f"https://meta-api.metalabs.work/api/v3/playtime/{project_name}/{server_name}/list"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params={"uuids[]": all_uuids})
        if response.status_code != 200:
            return {"error": "Ошибка при запросе онлайна"}

        data = response.json()
        if data.get("error") or "body" not in data:
            return {"error": "Ошибка API"}

        online_points = data["body"]

    # 🔹 Получаем текущий месяц и год
    current_date = datetime.now()
    current_year = str(current_date.year)
    current_month = f"{current_date.month:02d}"  # Двузначный формат месяца

    # 🔹 Обрабатываем данные
    activity_list = []
    for uuid in all_uuids:
        user_data = online_points.get(uuid, {})
        total_seconds = sum(
            time for date, time in user_data.get("onlinePoints", {}).items()
            if date.startswith(f"{current_year}-{current_month}")  # Фильтруем только за текущий месяц
        )

        # Конвертируем в ЧЧ:ММ
        hours, minutes = divmod(total_seconds // 60, 60)
        time_str = f"{hours}ч {minutes}м"
        total_minutes = hours * 60 + minutes  # Время в минутах для сортировки

        activity_list.append({
            "nickname": nicknames.get(uuid, uuid),
            "hours": time_str,
            "total_minutes": total_minutes
        })

    # 🔹 Сортируем по убыванию
    activity_list.sort(key=lambda x: x["total_minutes"], reverse=True)

    return {"activity": activity_list}


# ✅ **Функция получения онлайна за месяц**
async def get_monthly_playtime(project_name: str, server_name: str, user_uuid: str, _: str = Depends(require_login)) -> str:
    url = PLAYTIME_URL_TEMPLATE.format(project=project_name, server=server_name) + user_uuid
    headers = {"Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data.get('error') and 'body' in data and user_uuid in data['body']:
                online_points = data['body'][user_uuid].get('onlinePoints', {})

                # Получаем текущую дату и год/месяц
                current_date = datetime.now()
                year, month = current_date.year, current_date.month

                # Суммируем время онлайна за текущий месяц
                total_seconds = sum(
                    time for date, time in online_points.items() if date.startswith(f"{year}-{month:02d}")
                )

                # Конвертируем секунды в ЧЧ:ММ
                hours, minutes = divmod(total_seconds // 60, 60)
                return f"{hours}ч {minutes}м"

        return "Нет данных"

# ✅ **Функция получения UUID пользователя**
async def get_user_uuid(project_name: str, username: str, _: str = Depends(require_login)) -> str:
    url = f"{API_BASE_URL}/{project_name}/get/uuids"
    headers = {
        "Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"
    }
    params = {
        "nicks[]": username
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("body", {}).get(username, "UUID не найден")
        return "Ошибка UUID"
async def get_user_skin(project_name: str, user_uuid: str) -> str:
    return f"https://meta-api.metalabs.work/api/v3/users/skins/{project_name}/head/{user_uuid}"

@app.get("/get_splaytime")
async def get_splaytime(request: Request, nickname: str = Query(...), start_date: str = Query(...), end_date: str = Query(...), _: str = Depends(require_login)):
    """Возвращает время онлайна за заданный период"""
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    # Получаем UUID по нику
    uuid = await get_user_uuid(project_name, nickname)
    if uuid == "UUID не найден":
        return {"error": "Пользователь не найден"}

    # Формируем URL для запроса онлайна
    url = PLAYTIME_PERIOD_URL_TEMPLATE.format(project=project_name, server=server_name, min=start_date, max=end_date) + uuid
    headers = {"Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data.get('error') and 'body' in data and uuid in data['body']:
                online_points = data['body'][uuid].get('onlinePoints', {})

                # Суммируем общее время за период
                total_seconds = sum(online_points.values())

                # Переводим в часы и минуты
                hours, minutes = divmod(total_seconds // 60, 60)
                return {"nickname": nickname, "time": f"{hours}ч {minutes}м"}

    return {"error": "Не удалось получить данные"}

async def get_server_staff(project_name: str, server_name: str, _: str = Depends(require_login)):
    url = STAFF_URL_TEMPLATE.format(project=project_name, server=server_name)
    headers = {"Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data.get('error') and 'body' in data and 'users' in data['body']:
                users = data['body']['users']

                # Разбиваем по группам
                staff = {
                    "stmoderators": [],
                    "moderators": [],
                    "helpers": [],
                    "interns": []
                }

                for uuid, group in users.items():
                    if group == 'group.stmoderator':
                        staff["stmoderators"].append(uuid)
                    elif group == 'group.moder':
                        staff["moderators"].append(uuid)
                    elif group == 'group.helper':
                        staff["helpers"].append(uuid)
                    elif group == 'group.intern':
                        staff["interns"].append(uuid)

                return staff

    return None  # Ошибка или пустой состав


async def get_nicknames_by_uuids(uuids: list, project_name: str, _: str = Depends(require_login)):
    if not uuids:
        return {}
    print("1")
    url = f"{API_BASE_URL}/{project_name}/get/nicks"
    headers = {"Meta-Api-Key": "sATznYRhaQ1bDYAptTtXpsJXPCtsUP"}
    params = {"uuids[]": uuids}
    print(url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        print(response)
        if response.status_code == 200:
            data = response.json()
            return data.get("body", {})  # Возвращаем {uuid: nickname}

    return {}

@app.get("/staff", response_class=HTMLResponse)
async def staff_page(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    # Получаем состав сервера
    staff = await get_server_staff(project_name, server_name)

    if not staff:
        return templates.TemplateResponse("staff.html", {
            "request": request,
            "project_name": project_name,
            "server_name": server_name,
            "staff": None,
            "error": "Не удалось загрузить состав"
        })

    # Получаем UUID всех модераторов
    all_uuids = staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]
    print(all_uuids)

    # ✅ Получаем никнеймы по UUID
    nicknames = await get_nicknames_by_uuids(all_uuids, project_name)
    print(nicknames)

    # ✅ Заменяем UUID на никнеймы
    def replace_uuids_with_nicknames(uuid_list):
        return [nicknames.get(uuid, uuid) for uuid in uuid_list]

    staff["stmoderators"] = replace_uuids_with_nicknames(staff["stmoderators"])
    staff["moderators"] = replace_uuids_with_nicknames(staff["moderators"])
    staff["helpers"] = replace_uuids_with_nicknames(staff["helpers"])
    staff["interns"] = replace_uuids_with_nicknames(staff["interns"])

    return templates.TemplateResponse("staff.html", {
        "request": request,
        "project_name": project_name,
        "server_name": server_name,
        "staff": staff,
        "nicknames": nicknames
    })

@app.get("/get_staff")
async def get_staff(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    # Получаем состав сервера
    staff = await get_server_staff(project_name, server_name)

    if not staff:
        return {"error": "Не удалось загрузить состав"}

    # Получаем UUID всех модераторов
    all_uuids = staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]

    # Получаем никнеймы
    nicknames = await get_nicknames_by_uuids(all_uuids, project_name)

    # Заменяем UUID на никнеймы
    def replace_uuids_with_nicknames(uuid_list):
        return [nicknames.get(uuid, uuid) for uuid in uuid_list]

    staff["stmoderators"] = replace_uuids_with_nicknames(staff["stmoderators"])
    staff["moderators"] = replace_uuids_with_nicknames(staff["moderators"])
    staff["helpers"] = replace_uuids_with_nicknames(staff["helpers"])
    staff["interns"] = replace_uuids_with_nicknames(staff["interns"])

    return {"staff": staff}

