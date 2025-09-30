from typing import Optional
from app.core.security import hash_password, verify_password

# Временная "фейковая БД"
fake_users_db = {
    "killchik": {"username": "killchik", "hashed_password": hash_password("adminы")},
    "admin": {"username": "admin", "hashed_password": hash_password("password123")},
    "FearTerror": {"username": "FearTerror", "hashed_password": hash_password("admin")},
    "Seyllon": {"username": "Seyllon", "hashed_password": hash_password("AdminSeyllon")},
    "Tori_sss": {"username": "Tori_sss", "hashed_password": hash_password("admin")},
}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Проверка логина и пароля"""
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def get_current_user(username: str) -> Optional[dict]:
    return fake_users_db.get(username)
