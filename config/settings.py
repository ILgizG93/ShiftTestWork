import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from database import DataBaseServer

load_dotenv()

database: DataBaseServer = DataBaseServer(
    os.environ.get("DB_HOST"), 
    os.environ.get("DB_PORT"), 
    os.environ.get("DB_USER"), 
    os.environ.get("DB_PASS"), 
    os.environ.get("DB_NAME")
)

DB_ASYNC_URL = f"postgresql+asyncpg://{database.username}:{database.password}@{database.host}:{database.port}/{database.name}"


class Settings(BaseSettings):
    secret_key: str = os.environ.get("SECRET_KEY")
    algorithm: str = os.environ.get("ALGORITHM")
    access_token_expire_time: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 14)

    db_async_engine = create_async_engine(url=DB_ASYNC_URL, echo=False)
    db_async_session = async_sessionmaker(db_async_engine, class_=AsyncSession, expire_on_commit=False)

    async def get_db_session_async() -> AsyncGenerator[AsyncSession, None]:
        try:
            air_engine: AsyncEngine = create_async_engine(DB_ASYNC_URL)
            air_async_session = sessionmaker(air_engine, class_=AsyncSession, expire_on_commit=False)
            session: AsyncSession = air_async_session()
            yield session
        finally:
            await session.close()
