from typing import Annotated, Callable

from fastapi import Depends, Response, status
from sqlalchemy import UUID, Cast, Insert, Result, Select, String, insert, exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert

from config.settings import Settings
from loggers import init_logger
from src.handlers.password import hash_password
from src.models import Employees, Users
from src.schemas import User, UserCreate, UserSalary


settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]
logger = init_logger("app")


async def _user_create(
    body: UserCreate,
    session: DBSession
) -> User:
    body: dict = body.model_dump(exclude_none=True)
    employee_input: dict = {
        'full_name': body.pop('full_name'),
        'salary': body.pop('salary'),
        'next_raise_date': body.pop('next_raise_date')
    }
    try:
        async with session.begin():
            query: ReturningInsert = insert(Employees).values(**employee_input).returning(Employees.id)
            result: Result = await session.execute(query)
            employee: dict = dict(result.mappings().fetchone())

            body['password'] = hash_password(body.get('password'))
            body.update( {'employee_id': employee.get('id') } )

            query: Insert = insert(Users).values(**body)
            result = await session.execute(query)
            
            query: Select = select(
                Cast(Employees.id, String).label('employee_id'), Cast(Users.id, String).label('user_id'), 
                Users.login, Employees.full_name, Employees.salary, Employees.next_raise_date
            ).\
                join(Users, Users.employee_id == Employees.id).\
                where(Employees.id == employee.get('id'))
            result = await session.execute(query)
            response = result.mappings().fetchone()

            logger.info(f'Add user: {str(dict(response))}')
            
            return response
    except exc.SQLAlchemyError as err:
        logger.error(f'Add user: {err.args[0]}')
        return Response(
            content={ 'status_code': 500, 'error': err.args[0] }, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def _get_salary(
    user_id: UUID,
    session: DBSession
) -> UserSalary:
    query: Select = select(
        Cast(Employees.id, String).label('employee_id'), Cast(Users.id, String).label('user_id'), 
        Employees.salary, Employees.next_raise_date
    ).\
        join(Users, Users.employee_id == Employees.id).\
        where(Users.id == user_id)
    result: Result = await session.execute(query)
    if (response:= result.mappings().fetchone()):
        logger.info(f'Get user\'s salary: {str(dict(response))}')
        return response
    else:
        logger.info(f'User\'s (id = {str(user_id)}) salary not found')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

async def _login():
    pass

async def _logout():
    pass
