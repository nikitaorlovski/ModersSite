# app/services/staff_service.py
from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates
from app.database.salary_db import save_salary, get_salary, get_all_salaries
from app.services.telegram import send_salary_report
from app.services.metalabs import MetalabsService

metalabs_service = MetalabsService()

async def render_staff_page(request: Request, templates: Jinja2Templates):
    project = request.session.get("project_name", "Не выбран")
    server = request.session.get("server_name", "Не выбран")

    staff = await metalabs_service.get_server_staff(project, server)
    if not staff:
        return templates.TemplateResponse("staff.html", {
            "request": request,
            "project_name": project,
            "server_name": server,
            "staff": None,
            "error": "Не удалось загрузить состав"
        })

    nicknames = await metalabs_service.get_nicknames_by_uuids(
        staff["curators"] + staff["grandmoderators"] +
        staff["stmoderators"] + staff["moderators"] +
        staff["helpers"] + staff["interns"],
        project
    )
    staff = await metalabs_service.replace_uuids_with_nicknames(staff, nicknames)

    return templates.TemplateResponse("staff.html", {
        "request": request,
        "project_name": project,
        "server_name": server,
        "staff": staff,
        "nicknames": nicknames
    })

async def get_staff_json(request: Request):
    project = request.session.get("project_name")
    server = request.session.get("server_name")
    staff = await metalabs_service.get_server_staff(project, server)
    if not staff:
        return {"error": True, "message": "Не удалось загрузить состав"}
    return staff

async def save_salary_entry(data: dict):
    if not all(k in data for k in ["nickname", "role", "project", "server", "month", "total_salary"]):
        raise HTTPException(status_code=400, detail="Не все поля переданы")

    if not save_salary(data):
        raise HTTPException(status_code=500, detail="Ошибка при сохранении")
    return {"success": True}

async def get_salary_entry(nickname: str, project: str, server: str, month: str | None):
    salary = get_salary(nickname, project, server, month)
    if not salary:
        raise HTTPException(status_code=404, detail="Зарплата не найдена")
    return salary

async def send_salary_to_telegram(salary_data: dict):
    if not await send_salary_report(salary_data):
        raise HTTPException(status_code=500, detail="Ошибка отправки в Telegram")
    return {"success": True}
