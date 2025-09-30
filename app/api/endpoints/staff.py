from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.api.endpoints.auth import require_login
from app.services.metalabs import MetalabsService
from app.services.telegram import send_salary_report, send_custom_message
from app.database.base import get_db
from app.database import crud, schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
metalabs_service = MetalabsService()


# ----------------- SALARIES ----------------- #

@router.post("/save_salary")
async def save_staff_salary(
    data: schemas.SalaryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Сохранение или обновление зарплаты модератора"""
    try:
        salary = await crud.create_or_update_salary(db, data)
        return {"success": True, "salary": salary.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_salary/{nickname}", response_model=schemas.SalaryOut)
async def get_staff_salary(
    nickname: str,
    project: str,
    server: str,
    month: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    salary = await crud.get_salary(db, nickname, project, server, month)
    if not salary:
        raise HTTPException(status_code=404, detail="Зарплата не найдена")
    return salary


@router.get("/get_all_salaries", response_model=list[schemas.SalaryOut])
async def get_staff_salaries(
    project: str,
    server: str,
    month: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_all_salaries(db, project, server, month)


@router.post("/get_salaries")
async def get_salaries(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """Эквивалент старого get_salaries для фронта"""
    project = payload.get("project")
    server = payload.get("server")
    month = payload.get("month")
    return await crud.get_all_salaries(db, project, server, month)


@router.post("/delete_salary")
async def delete_salary(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_salary(
        db,
        payload["nickname"],
        payload["project"],
        payload["server"],
        payload["month"]
    )
    return {"success": success}


@router.post("/send_full_salary_report")
async def send_full_salary_report(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """Формирование и отправка полного отчета в Telegram"""
    project = payload.get("project")
    server = payload.get("server")
    month = payload.get("month")

    salaries = await crud.get_all_salaries(db, project, server, month)
    if not salaries:
        return {"error": "Нет зарплат для отправки"}

    # Разделение по статусу
    psj_staff = [s for s in salaries if s.role == "ПСЖ"]
    active_staff = [s for s in salaries if s.role != "ПСЖ"]

    role_priority = {
        "Гл.модератор": 1,
        "Ст.модератор": 2,
        "Модератор": 3,
        "Хелпер": 4,
        "Стажер": 5
    }

    def sort_key(staff):
        return role_priority.get(staff.role, 999), staff.nickname

    active_staff.sort(key=sort_key)

    header = f"\nПроект {project}\nСервер {server}\nМесяц {month}\n\n"

    active_lines = [
        f"{s.role} {s.nickname} — {int(s.total_salary)} рубинов"
        for s in active_staff
    ]

    psj_lines = [
        f"{s.nickname} — {int(s.total_salary)} рубинов"
        for s in psj_staff
    ]

    # Топ вопрос-ответ
    top_questions = sorted(
        [s for s in active_staff if s.questions_top in [1, 2, 3]],
        key=lambda x: x.questions_top
    )

    question_bonus_lines = [
        f"{s.nickname} — +{15 if s.questions_top == 1 else 10 if s.questions_top == 2 else 5}% "
        f"к зарплате ({s.questions_top} место)"
        for s in top_questions
    ]

    # Топ онлайн
    top_online = sorted(
        [s for s in active_staff if s.online_top in [1, 2, 3]],
        key=lambda x: x.online_top
    )

    online_bonus_lines = [
        f"{s.nickname} — +{15 if s.online_top == 1 else 10 if s.online_top == 2 else 5}% "
        f"к зарплате ({s.online_top} место)"
        for s in top_online
    ]

    full_message = header + "\n".join(active_lines)

    if question_bonus_lines:
        full_message += "\n\nТОП ВОПРОС-ОТВЕТ:\n\n" + "\n".join(question_bonus_lines)

    if online_bonus_lines:
        full_message += "\n\nТОП ОНЛАЙН:\n\n" + "\n".join(online_bonus_lines)

    if psj_lines:
        full_message += "\n\nПСЖ:\n" + "\n".join(psj_lines)

    success = await send_custom_message(full_message)
    if not success:
        return {"error": "Ошибка при отправке в Telegram"}

    return {"success": True}


@router.post("/send_salary_telegram")
async def send_staff_salary_telegram(salary_data: dict):
    """Отправка отчета о зарплате в Telegram"""
    success = await send_salary_report(salary_data)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка при отправке в Telegram")
    return {"success": True}


# ----------------- STAFF & METALABS ----------------- #

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

@router.get("/get_staff")
async def get_staff(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    staff = await metalabs_service.get_server_staff(project_name, server_name)
    if not staff:
        return {"error": True, "message": "Не удалось загрузить состав"}

    all_uuids = sum(staff.values(), [])
    nicknames = await metalabs_service.get_nicknames_by_uuids(all_uuids, project_name)

    users = {}
    mapping = {
        "curators": "group.curator",
        "grandmoderators": "group.grandmoderator",
        "stmoderators": "group.stmoderator",
        "moderators": "group.moder",
        "helpers": "group.helper",
        "interns": "group.stajer"
    }

    for role, uuids in staff.items():
        for uuid in uuids:
            users[nicknames.get(uuid, uuid)] = mapping[role]

    return {"body": {"users": users}}

@router.get("/get_moderator_activity")
async def get_moderator_activity(request: Request, _: str = Depends(require_login)):
    project_name = request.session.get("project_name", "Не выбран")
    server_name = request.session.get("server_name", "Не выбран")

    if not project_name or not server_name:
        return {"error": "Проект или сервер не выбраны. Пожалуйста, выберите заново."}

    staff = await metalabs_service.get_server_staff(project_name, server_name)
    if not staff:
        return {"error": "Не удалось загрузить состав модераторов"}

    all_uuids = sum(staff.values(), [])
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

    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    result = await metalabs_service.get_playtime_period(
        project_name, server_name, nickname, start_date, end_date
    )
    return result
