from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.database import schemas, crud
from app.database.base import get_db

router = APIRouter()


@router.post("/save_table_data")
async def save_table_data(
    data: schemas.StaffTableDataCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_or_update_table_data(db, data)

@router.get("/get_table_data")
async def get_table_data(
    project: str,
    server: str, 
    month: str,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_table_data(db, project, server, month)

# routers/table.py - добавить
@router.post("/save_table_data_batch")
async def save_table_data_batch(
    data: list[schemas.StaffTableDataCreate],
    db: AsyncSession = Depends(get_db)
):
    """Сохранение нескольких записей таблицы"""
    results = []
    for item in data:
        result = await crud.create_or_update_table_data(db, item)
        results.append(result)
    return results