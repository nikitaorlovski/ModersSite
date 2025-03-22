import asyncpg
import bcrypt
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://moders_user:hH2MO7EcWcV23zNwJEX5FlmpNuuhqGeC@dpg-cvffdcdds78s73fl7o9g-a/moders_db")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=DB_URL)

    async def create_users_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                );
            """)

    async def add_user(self, username: str, password: str):
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (username, password_hash) VALUES ($1, $2)",
                username, password_hash
            )

    async def verify_user(self, username: str, password: str) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT password_hash FROM users WHERE username = $1",
                username
            )
            if row:
                return bcrypt.checkpw(password.encode(), row['password_hash'].encode())
            return False

    async def user_exists(self, username: str) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1 FROM users WHERE username = $1", username)
            return result is not None

db = Database()