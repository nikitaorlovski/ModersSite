from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import event

DATABASE_URL = "sqlite+aiosqlite:///./salaries.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

async_session: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

# Dependency для FastAPI
async def get_db():
    async with async_session() as session:
        yield session
