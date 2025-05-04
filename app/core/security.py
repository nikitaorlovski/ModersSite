from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return to_encode 

# Хеширование пароля
hashed_password = hash_password("your_password")

# Проверка пароля
if verify_password("your_password", hashed_password):
    print("Пароль верный")
else:
    print("Пароль неверный") 