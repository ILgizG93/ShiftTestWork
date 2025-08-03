from datetime import UTC, datetime, timedelta
from typing import Annotated, Callable
import logging

import jwt
from fastapi import Depends, Response, status
from sqlalchemy import Result, insert, exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningInsert

from config.settings import Settings
from loggers import init_logger
from src.models import Tokens
from src.schemas import TokenAfterCreate, TokenCreate


TOKEN_TYPE_FIELD: str = "type"
ACCESS_TOKEN_TYPE: str = "access"
REFRESH_TOKEN_TYPE: str = "refresh"

settings: Settings = Settings()
session: Callable = settings.database.get_session_async
DBSession = Annotated[AsyncSession, Depends(session)]
logger: logging = init_logger("app")

def encode_jwt(
    payload: dict,
    private_key: str = settings.private_key_file.read_text(),
    algorithm: str = settings.algorithm,
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
) -> str:
    current_datetime: datetime = datetime.now(UTC)
    to_encode: dict = payload.copy()
    if expire_timedelta:
        expire: datetime = current_datetime+expire_timedelta
    else:
        expire: datetime = current_datetime+timedelta(minutes=expire_minutes)
    to_encode.update(
        iat=current_datetime,
        exp=expire
    )
    encoded: str = jwt.encode(
        to_encode,
        private_key,
        algorithm
    )
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.public_key_file.read_text(),
    algorithm: str = settings.algorithm
) -> dict:
    decoded: dict = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded

def create_jwt(
    token_type: str, 
    token_data: dict,
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload: dict = { TOKEN_TYPE_FIELD: token_type }
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )

def create_access_token(user: dict) -> str:
    jwt_payload: dict = {
        "sub": user.get('user_id'),
        "user_id": user.get('user_id'),
        "login": user.get('login')
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.access_token_expire_minutes
    )

def create_refresh_token(user: dict) -> str:
    jwt_payload: dict = {
        "sub": user.get('user_id'),
        "user_id": user.get('user_id')
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.refresh_token_expire_days)
    )

async def save_token_in_db(
    body: TokenCreate,
    session: DBSession
) -> TokenAfterCreate:
    body: dict = body.model_dump(exclude_none=True)
    try:
        async with session.begin():
            query: ReturningInsert = insert(Tokens).values(**body).\
                returning(Tokens.id, Tokens.user_id, Tokens.token, Tokens.expires_at, Tokens.is_active)
            result: Result = await session.execute(query)
            token: dict = dict(result.mappings().one())

            logger.info(f'Save token with id {str(token.get("id"))!r}')
            
            return token
    except exc.SQLAlchemyError as err:
        logger.error(f'Save token: {err.args[0]}')
        return Response(
            content={ 'status_code': 500, 'error': err.args[0] }, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
