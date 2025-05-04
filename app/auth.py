from typing import Optional
from app.core.security import hash_password, verify_password

# В реальном приложении это должно быть в базе данных
fake_users_db = {
    "killchik": {"username": "killchik", "hashed_password": hash_password("adminы")},
    "admin": {"username": "admin", "hashed_password": hash_password("password123")},
    "FearTerror": {"username": "FearTerror", "hashed_password": hash_password("admin")},
    "Seyllon": {"username": "Seyllon", "hashed_password": hash_password("AdminSeyllon")},
    "Tori_sss": {"username": "Tori_sss", "hashed_password": hash_password("admin")},
}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def get_current_user(username: str):
    return fake_users_db.get(username)
