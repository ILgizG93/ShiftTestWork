from datetime import datetime
from functools import partial
import logging
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import UUID, Cast, Insert, Result, Select, String, insert, exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert
from jwt.exceptions import InvalidTokenError

from config.settings import Settings
from loggers import init_logger
from src.handlers.token import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD, create_access_token, create_refresh_token, decode_jwt, save_token_in_db
from src.handlers.password import hash_password, verify_password
from src.models import Employees, Users
from src.schemas import Token, TokenCreate, User, UserAuth, UserCreate, UserSalary


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
    user_auth: UserAuth,
    session: DBSession
) -> Token:
    query: Select = select(Cast(Users.id, String).label('user_id'), Users.login, Users.password).where(Users.login == user_auth.login)
    result: Result = await session.execute(query)
    if (response:= result.mappings().fetchone()):
        password: str = user_auth.password
        user: dict = dict(response)
        hashed_password: str = user.pop('password')
        if (verify_password(password, hashed_password.encode())):
            logger.info(f'Get user: {str(user)}')
            access_token: str = create_access_token(user)
            refresh_token: str = create_refresh_token(user)
            payload: dict = decode_jwt(token=access_token)
            token: TokenCreate = TokenCreate(
                user_id=payload.get('user_id'),
                token=access_token,
                expires_at=datetime.fromtimestamp(payload.get('exp'))
            )
            await session.close()
            await save_token_in_db(token, session)
            return Token(
                access_token=access_token,
                refresh_token=refresh_token
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def validate_current_token(token_type: str, current_token_type: str):
    if (current_token_type != token_type):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {current_token_type!r} expected {token_type!r}"
        )

def get_current_user(
    token_type: str,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> dict:
    try:
        payload: dict = decode_jwt(token=credentials.credentials)
        current_token_type: str = payload.get(TOKEN_TYPE_FIELD)
        validate_current_token(token_type, current_token_type)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error"
        )
    return payload

protected_access = partial(get_current_user, token_type=ACCESS_TOKEN_TYPE)
protected_refresh = partial(get_current_user, token_type=REFRESH_TOKEN_TYPE)

def login_required(
    user: dict = Depends(protected_access)
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
