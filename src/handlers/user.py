from typing import Annotated, Callable

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import UUID, Cast, CursorResult, Insert, RowMapping, Select, String, insert, exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from loggers import init_logger
from src.handlers.password import hash_password
from src.models import Employees, Users
from src.schemas import UserCreate


settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]
logger = init_logger("app")


async def _user_create(
    body: UserCreate,
    session: DBSession
) -> JSONResponse:
    body: dict = body.model_dump(exclude_none=True)
    employee: dict = {
        'full_name': body.pop('full_name'),
        'salary': body.pop('salary'),
        'next_raise_date': body.pop('next_raise_date')
    }
    try:
        query: Insert = insert(Employees).values(**employee).returning(Employees.id)
        result: CursorResult = await session.execute(query)
        employee: RowMapping = result.mappings().fetchone()

        body['password'] = hash_password(body.get('password'))
        body.update( {'employee_id': employee.id } )
        query = insert(Users).values(**body).returning(Cast(Users.id, String).label('id'), Users.login)
        
        result: CursorResult = await session.execute(query)
        user: dict = dict(result.mappings().fetchone())
        user.update( { 'status_code': 200 } )
        await session.commit()
        logger.info(f'Add user: {str(body)}')
        return JSONResponse(
            content=user
        )
    except exc.SQLAlchemyError as err:
        await session.rollback()
        logger.error(f'Add user: {err.args[0]}')
        return JSONResponse(
            content={ 'status_code': 500, 'error': err.args[0] }, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def _get_salary(
    employee_id: UUID,
    session: DBSession
) -> JSONResponse:
    query: Select = select(Employees.id, Employees.salary, Employees.full_name, Employees.next_raise_date).\
        where(Employees.id == employee_id)
    result: CursorResult = await session.execute(query)
    if (result:= result.mappings().fetchone()):
        salary: dict = dict(result)
        logger.info(f'Get employee\'s salary: {str(salary)}')
        return salary
    else:
        logger.info(f'Employee\'s (id = {str(employee_id)}) salary not found')
        return JSONResponse(
            content={ 'status_code': 404 }, 
            status_code=status.HTTP_404_NOT_FOUND
        )
