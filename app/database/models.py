from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, UniqueConstraint, DateTime
from datetime import datetime
from .base import Base

class Salary(Base):
    __tablename__ = "salaries"
    __table_args__ = (
        UniqueConstraint("nickname", "project", "server", "month", name="unique_salary"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, nullable=False)
    role = Column(String, nullable=False)
    project = Column(String, nullable=False)
    server = Column(String, nullable=False)
    online_hours = Column(Integer, default=0)
    questions = Column(Integer, default=0)
    complaints = Column(Integer, default=0)
    severe_complaints = Column(Integer, default=0)
    attached_moderators = Column(Integer, default=0)
    interviews = Column(Integer, default=0)
    online_top = Column(Integer, nullable=True)
    questions_top = Column(Integer, nullable=True)
    gma_review = Column(Integer, default=0)
    total_salary = Column(Float, nullable=False)
    month = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# models.py - добавить
class StaffTableData(Base):
    __tablename__ = "staff_table_data"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, index=True)
    project = Column(String, index=True)
    server = Column(String, index=True)
    month = Column(String, index=True)  # формат "2025-01"

    # Данные которые заполняют старшие модераторы
    online_hours = Column(Integer, default=0)
    questions = Column(Integer, default=0)
    complaints = Column(Integer, default=0)
    severe_complaints = Column(Integer, default=0)
    attached_moderators = Column(Integer, default=0)
    interviews = Column(Integer, default=0)
    online_top = Column(Integer, nullable=True)  # 1,2,3 или NULL
    questions_top = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)