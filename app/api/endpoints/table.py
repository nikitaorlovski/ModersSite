# routers/table.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import require_login, templates
from app.database.base import get_db
from app.database import crud, schemas

router = APIRouter()

@router.get("/get_table_data")
async def get_table_data(
    project: str,
    server: str, 
    month: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение данных таблицы для проекта, сервера и месяца"""
    try:
        data = await crud.get_table_data(db, project, server, month)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save_table_data")
async def save_table_data(
    data: schemas.StaffTableDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Сохранение или обновление данных таблицы"""
    try:
        result = await crud.create_or_update_table_data(db, data)
        return {"success": True, "id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save_table_data_batch")
async def save_table_data_batch(
    data: list[schemas.StaffTableDataCreate],
    db: AsyncSession = Depends(get_db)
):
    """Сохранение нескольких записей таблицы"""
    try:
        results = []
        for item in data:
            result = await crud.create_or_update_table_data(db, item)
            results.append(result.id)
        return {"success": True, "saved_ids": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/table_page/{project_name}/{server_name}")
async def table_page(
    request: Request,
    project_name: str,
    server_name: str,
    _: str = Depends(require_login)
):
    return templates.TemplateResponse("table_page.html", {
        "request": request,
        "project_name": project_name,
        "server_name": server_name
    })