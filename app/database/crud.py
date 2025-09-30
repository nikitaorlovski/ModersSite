from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Salary, StaffTableData
from .schemas import SalaryCreate, StaffTableDataCreate


async def create_or_update_salary(db: AsyncSession, data: SalaryCreate):
    query = (
        select(Salary)
        .where(Salary.nickname == data.nickname)
        .where(Salary.project == data.project)
        .where(Salary.server == data.server)
        .where(Salary.month == data.month)
    )
    result = await db.execute(query)
    salary = result.scalar_one_or_none()

    if salary:  # обновляем
        for field, value in data.dict().items():
            setattr(salary, field, value)
    else:  # создаем
        salary = Salary(**data.dict())
        db.add(salary)

    await db.commit()
    await db.refresh(salary)
    return salary

async def get_salary(db: AsyncSession, nickname: str, project: str, server: str, month: str):
    query = select(Salary).where(
        Salary.nickname == nickname,
        Salary.project == project,
        Salary.server == server,
        Salary.month == month
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_all_salaries(db: AsyncSession, project: str, server: str, month: str = None):
    query = select(Salary).where(
        Salary.project == project,
        Salary.server == server
    )
    if month:
        query = query.where(Salary.month == month)

    result = await db.execute(query)
    return result.scalars().all()

async def delete_salary(db: AsyncSession, nickname: str, project: str, server: str, month: str):
    query = select(Salary).where(
        Salary.nickname == nickname,
        Salary.project == project,
        Salary.server == server,
        Salary.month == month
    )
    result = await db.execute(query)
    salary = result.scalar_one_or_none()

    if not salary:
        return False

    await db.delete(salary)
    await db.commit()
    return True


# crud.py - добавить
async def create_or_update_table_data(db: AsyncSession, data: StaffTableDataCreate):
    # Поиск существующей записи
    query = select(StaffTableData).where(
        StaffTableData.nickname == data.nickname,
        StaffTableData.project == data.project,
        StaffTableData.server == data.server,
        StaffTableData.month == data.month
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Обновляем существующую
        for field, value in data.dict().items():
            setattr(existing, field, value)
    else:
        # Создаем новую
        existing = StaffTableData(**data.dict())
        db.add(existing)

    await db.commit()
    await db.refresh(existing)
    return existing


# crud.py - исправляем функцию get_table_data
# crud.py - временное решение
async def get_table_data(db: AsyncSession, project: str, server: str, month: str):
    try:
        query = select(StaffTableData).where(
            StaffTableData.project == project,
            StaffTableData.server == server,
            StaffTableData.month == month
        )
        result = await db.execute(query)
        staff_data = result.scalars().all()

        # Если нет данных - верни пустой массив
        if not staff_data:
            return []

        # Преобразуем в словари
        return [
            {
                "nickname": item.nickname,
                "online_hours": item.online_hours,
                "questions": item.questions,
                "complaints": item.complaints,
                "severe_complaints": item.severe_complaints,
                "attached_moderators": item.attached_moderators,
                "interviews": item.interviews,
                "online_top": item.online_top,
                "questions_top": item.questions_top
            }
            for item in staff_data
        ]
    except Exception as e:
        print(f"Error in get_table_data: {e}")
        return []  # В случае ошибки верни пустой массив

# crud.py - добавить эту функцию
async def get_table_data_by_nickname(db: AsyncSession, nickname: str, project: str, server: str, month: str):
    query = select(StaffTableData).where(
        StaffTableData.nickname == nickname,
        StaffTableData.project == project,
        StaffTableData.server == server,
        StaffTableData.month == month
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()