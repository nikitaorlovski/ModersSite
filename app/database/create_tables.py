# create_tables.py
import asyncio
import sys
import os

# Добавь путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base, engine
from app.database.models import Salary, StaffTableData

async def create_tables():
    print("Создаем таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем старые таблицы
        await conn.run_sync(Base.metadata.create_all)  # Создаем новые
    print("✅ Все таблицы созданы!")

if __name__ == "__main__":
    asyncio.run(create_tables())