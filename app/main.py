from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from app.core.config import get_settings
from app.api.endpoints import auth, projects, staff
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_password
from typing import Optional

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str) -> Optional[dict]:
    # В текущей реализации с сессиями эта функция не нужна
    # Она будет полезна при переходе на JWT-токены
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


