from typing import Annotated, Callable
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from src.handlers.user import _get_salary, _user_create
from src.schemas import UserCreate


settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]

router: APIRouter = APIRouter()


@router.post("/user/create", response_class=JSONResponse)
async def user_create(body: UserCreate, session: DBSession) -> JSONResponse:
    return await _user_create(body, session)

@router.post("/user/{user_id}/salary/get")
async def get_salary(user_id: UUID, session: DBSession) -> JSONResponse:
    return await _get_salary(user_id, session)
