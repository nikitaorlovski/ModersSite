from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.endpoints.auth import require_login
from app.services.metalabs import MetalabsService
from app.services.telegram import send_salary_report
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.core.config import get_settings
from ...database.salary_db import save_salary, get_salary, get_all_salaries, init_db

init_db()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
metalabs_service = MetalabsService()

@router.post("/delete_salary")
def delete_salary(payload: dict):
    from app.database.salary_db import delete_salary_record
    success = delete_salary_record(
        payload["nickname"],
        payload["project"],
        payload["server"],
        payload["month"]
    )
    return {"success": success}

@router.post("/get_salaries")
def get_salaries(payload: dict):
    project = payload.get("project")
    server = payload.get("server")
    month = payload.get("month")

    return get_all_salaries(project, server, month)
@router.post("/send_full_salary_report")
async def send_full_salary_report(payload: dict):
    project = payload.get("project")
    server = payload.get("server")
    month = payload.get("month")

    salaries = get_all_salaries(project, server, month)
    if not salaries:
        return {"error": "Нет зарплат для отправки"}

    # Разделяем
    psj_staff = [s for s in salaries if s.get("role") == "ПСЖ"]
    active_staff = [s for s in salaries if s.get("role") != "ПСЖ"]

    # Приоритет по ролям
    role_priority = {
        "Гл.модератор": 1,
        "Ст.модератор": 2,
        "Модератор": 3,
        "Хелпер": 4,
        "Стажер": 5
    }

    def sort_key(staff):
        return role_priority.get(staff.get("role"), 999), staff.get("nickname", "")

    active_staff.sort(key=sort_key)

    # Сообщение
    header = f"\nСервер {server}\nМесяц {month}\n\n"

    active_lines = [
        f"{s['role']} {s['nickname']} — {int(s['total_salary'])} рубинов"
        for s in active_staff
    ]

    psj_lines = [
        f"{s['nickname']} — {int(s['total_salary'])} рубинов"
        for s in psj_staff
    ]

    # Топ по вопросам
    top_questions = sorted(
        [s for s in active_staff if s.get("questions_top") in [1, 2, 3]],
        key=lambda x: x["questions_top"]
    )

    question_bonus_lines = [
        f"{s['nickname']} — +{15 if s['questions_top']==1 else 10 if s['questions_top']==2 else 5}% к зарплате"
        for s in top_questions
    ]

    # Топ по онлайну
    top_online = sorted(
        [s for s in active_staff if s.get("online_top") in [1, 2, 3]],
        key=lambda x: x["online_top"]
    )

    online_bonus_lines = [
        f"{s['nickname']} — +{15 if s['online_top']==1 else 10 if s['online_top']==2 else 5}% к зарплате"
        for s in top_online
    ]

    # Итоговое сообщение
    full_message = header + "\n".join(active_lines)

    if question_bonus_lines:
        full_message += "\n\nТОП ВОПРОС-ОТВЕТ:\n\n" + "\n".join(question_bonus_lines)

    if online_bonus_lines:
        full_message += "\n\nТОП ОНЛАЙН:\n\n" + "\n".join(online_bonus_lines)

    if psj_lines:
        full_message += "\n\nПСЖ:\n" + "\n".join(psj_lines)

    # Отправка
    from app.services.telegram import send_custom_message
    success = await send_custom_message(full_message)
    return {"success": success}

class SalaryData(BaseModel):
    nickname: str
    role: str
    project: str
    server: str
    online_hours: int
    questions: int
    complaints: int
    severe_complaints: int
    attached_moderators: int
    interviews: int
    online_top: Optional[int] = None
    questions_top: Optional[int] = None
    gma_review: int
    total_salary: float
    month: str

@router.get("/server/{project_name}/{server_name}")
async def select_server(request: Request, project_name: str, server_name: str, _: str = Depends(require_login)):
    request.session["project_name"] = project_name
    request.session["server_name"] = server_name
    username = request.session.get("username", "Неизвестно")

    user_uuid = await metalabs_service.get_user_uuid(project_name, username)
    user_skin_url = await metalabs_service.get_user_skin(project_name, user_uuid)
    monthly_playtime = await metalabs_service.get_monthly_playtime(project_name, server_name, user_uuid)

    return templates.TemplateResponse("server_details.html", {
        "request": request,
        "server_name": server_name,
        "project_name": project_name,
        "user_skin_url": user_skin_url,
        "user_uuid": user_uuid,
        "username": username,
        "monthly_playtime": monthly_playtime
    })

@router.get("/get_moderator_activity")
async def get_moderator_activity(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")
    
    if not project_name or not server_name:
        return {"error": "Проект или сервер не выбраны. Пожалуйста, выберите заново."}

    staff = await metalabs_service.get_server_staff(project_name, server_name)
    if not staff:
        return {"error": "Не удалось загрузить состав модераторов"}

    all_uuids = staff["curators"] + staff["grandmoderators"] + staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]
    nicknames = await metalabs_service.get_nicknames_by_uuids(all_uuids, project_name)

    activity_list = await metalabs_service.get_staff_activity(project_name, server_name, all_uuids, nicknames)
    return {"activity": activity_list}

@router.get("/get_splaytime")
async def get_splaytime(
    request: Request, 
    nickname: str = Query(...), 
    start_date: str = Query(...), 
    end_date: str = Query(...), 
    _: str = Depends(require_login)
):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    result = await metalabs_service.get_playtime_period(project_name, server_name, nickname, start_date, end_date)
    return result

@router.get("/staff", response_class=HTMLResponse)
async def staff_page(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    staff = await metalabs_service.get_server_staff(project_name, server_name)
    if not staff:
        return templates.TemplateResponse("staff.html", {
            "request": request,
            "project_name": project_name,
            "server_name": server_name,
            "staff": None,
            "error": "Не удалось загрузить состав"
        })

    all_uuids = staff["curators"] + staff["grandmoderators"] + staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]
    nicknames = await metalabs_service.get_nicknames_by_uuids(all_uuids, project_name)

    staff = await metalabs_service.replace_uuids_with_nicknames(staff, nicknames)

    return templates.TemplateResponse("staff.html", {
        "request": request,
        "project_name": project_name,
        "server_name": server_name,
        "staff": staff,
        "nicknames": nicknames
    })

@router.get("/get_staff")
async def get_staff(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    staff = await metalabs_service.get_server_staff(project_name, server_name)
    if not staff:
        return {"error": True, "message": "Не удалось загрузить состав"}

    all_uuids = staff["curators"] + staff["grandmoderators"] + staff["stmoderators"] + staff["moderators"] + staff["helpers"] + staff["interns"]
    nicknames = await metalabs_service.get_nicknames_by_uuids(all_uuids, project_name)

    # Преобразуем формат данных для клиента
    users = {}
    for role, uuids in staff.items():
        role_prefix = {
            "curators": "group.curator",
            "grandmoderators": "group.grandmoderator",
            "stmoderators": "group.stmoderator",
            "moderators": "group.moder",
            "helpers": "group.helper",
            "interns": "group.stajer"
        }[role]
        
        for uuid in uuids:
            users[nicknames.get(uuid, uuid)] = role_prefix

    return {"body": {"users": users}}

@router.get("/check_online")
async def check_online(
    request: Request,
    nickname: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    _: str = Depends(require_login)
):
    project_name = request.session.get("project_name")
    server_name = request.session.get("server_name")

    if not project_name or not server_name:
        return {"error": "Проект или сервер не выбраны. Пожалуйста, выберите заново."}

    # Если даты не переданы — подставляем текущую дату
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    result = await metalabs_service.get_playtime_period(
        project_name, server_name, nickname, start_date, end_date
    )
    return result


@router.post("/save_salary")
async def save_staff_salary(data: dict):
    """Сохранение зарплаты модератора"""
    try:
        print("Получены данные в эндпоинте:", data)
        
        required_fields = ['nickname', 'role', 'project', 'server', 'month', 'total_salary']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Отсутствует обязательное поле: {field}")
        
        success = save_salary(data)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")
    except Exception as e:
        print("Ошибка в эндпоинте save_salary:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_salary/{nickname}")
async def get_staff_salary(
    nickname: str, 
    project: str,
    server: str,
    month: Optional[str] = None
):
    try:
        salary = get_salary(nickname, project, server, month)
        if salary:
            return salary
        raise HTTPException(status_code=404, detail="Зарплата не найдена")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_salaries")
async def get_staff_salaries(
    project: str,
    server: str,
    month: Optional[str] = None
):
    try:
        return get_all_salaries(project, server, month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send_salary_telegram")
async def send_staff_salary_telegram(salary_data: dict):
    """Отправка отчета о зарплате в Telegram"""
    try:
        success = await send_salary_report(salary_data)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Ошибка при отправке в Telegram")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 