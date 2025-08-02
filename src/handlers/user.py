import logging
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Response, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import UUID, Cast, Insert, Result, Select, String, insert, exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert
from jwt.exceptions import InvalidTokenError

from config.settings import Settings
from loggers import init_logger
from src.handlers.token import decode_jwt, encode_jwt
from src.handlers.password import hash_password, verify_password
from src.models import Employees, Users
from src.schemas import Token, User, UserAuth, UserCreate, UserSalary


settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]
logger: logging = init_logger("app")
http_bearer = HTTPBearer()


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

            body['password'] = hash_password(body.get('password')).decode()
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

async def _user_token_get(
    user: UserAuth,
    session: DBSession
) -> Token:
    query: Select = select(Cast(Users.id, String).label('user_id'), Users.login, Users.password).where(Users.login == user.login)
    result: Result = await session.execute(query)
    if (response:= result.mappings().fetchone()):
        password: str = user.password
        response: dict = dict(response)
        hashed_password: str = response.pop('password')
        if (verify_password(password, hashed_password.encode())):
            logger.info(f'Get user: {str(response)}')
            jwt_payload: dict = {
                "sub": response.get('user_id'),
                "user_id": response.get('user_id'),
                "login": response.get('login')
            }
            return Token(
                token_type='Bearer',
                access_token=encode_jwt(jwt_payload)
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

def current_user_get(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> dict:
    try:
        payload: dict = decode_jwt(token=credentials.credentials)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error"
        )
    return payload

def login_required(
    user: dict = Depends(current_user_get)
) -> dict:
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def _user_salary_get(
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
