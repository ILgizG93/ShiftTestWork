from typing import Annotated, Callable

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from src.handlers.user import _user_create, _user_token_get, _user_salary_get, login_required
from src.schemas import Token, User, UserCreate, UserSalary


settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]

router: APIRouter = APIRouter()


@router.post("/user/create", status_code=status.HTTP_201_CREATED, response_model=User)
async def user_create(
    body: UserCreate, 
    session: DBSession
) -> User:
    return await _user_create(body, session)

@router.post("/user/login")
async def user_login(
    token: dict = Depends(_user_token_get)
) -> Token:
    return token

@router.get("/user/salary/get", response_model=UserSalary)
async def user_salary_get(
    session: DBSession,
    user: dict = Depends(login_required)
) -> UserSalary | None:
    return await _user_salary_get(user.get('user_id'), session)
