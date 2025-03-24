from typing import Optional

fake_users_db = {
    "killchik": {"username": "killchik", "password": "adminы"},
    "admin": {"username": "admin", "password": "password123"},
    "FearTerror": {"username": "FearTerror", "password": "admin"},
    "Tori_sss": {"username": "Tori_sss", "password": "admin"},
}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return None
    return user

def get_current_user(username: str):
    return fake_users_db.get(username)
