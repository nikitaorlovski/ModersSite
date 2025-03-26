from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from app.core.config import get_settings
from app.api.endpoints import auth, projects, staff

settings = get_settings()

app = FastAPI()

# Настройка статических файлов
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Настройка сессий
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Подключаем роуты
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(staff.router)

