from pydantic import BaseModel
from typing import Optional

class SalaryBase(BaseModel):
    nickname: str
    role: str
    project: str
    server: str
    online_hours: int = 0
    questions: int = 0
    complaints: int = 0
    severe_complaints: int = 0
    attached_moderators: int = 0
    interviews: int = 0
    online_top: Optional[int] = None
    questions_top: Optional[int] = None
    gma_review: int = 0
    total_salary: float
    month: str

class SalaryCreate(SalaryBase):
    pass

class SalaryOut(SalaryBase):
    id: int
    class Config:
        orm_mode = True

# schemas.py - добавить
class StaffTableDataCreate(BaseModel):
    nickname: str
    project: str
    server: str
    month: str
    online_hours: int = 0
    questions: int = 0
    complaints: int = 0
    severe_complaints: int = 0
    attached_moderators: int = 0
    interviews: int = 0
    online_top: Optional[int] = None
    questions_top: Optional[int] = None

class StaffTableDataUpdate(BaseModel):
    online_hours: Optional[int] = None
    questions: Optional[int] = None
    complaints: Optional[int] = None
    severe_complaints: Optional[int] = None
    attached_moderators: Optional[int] = None
    interviews: Optional[int] = None
    online_top: Optional[int] = None
    questions_top: Optional[int] = None