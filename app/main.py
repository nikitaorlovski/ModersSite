from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from app.core.config import get_settings
from app.api.endpoints import auth, projects, staff, table
from app.database.base import Base, engine

settings = get_settings()

app = FastAPI(title="Moderators Site")

# Настройка статических файлов
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Настройка сессий
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(staff.router)
app.include_router(table.router, tags=["table"])

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы базы данных проверены/созданы")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
