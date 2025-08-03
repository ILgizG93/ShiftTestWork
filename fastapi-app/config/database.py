from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine

@dataclass
class Server:
    host: str
    port: str
    username: str
    password: str

    def __init__(self, *args) -> None:
        self.host = args[0]
        self.port = args[1]
        self.username = args[2]
        self.password = args[3]


@dataclass
class DataBaseServer(Server):
    name: str
    _url_async: str

    def __init__(self, *args) -> None:
        super().__init__(args[0], args[1], args[2], args[3])
        self.name = args[4]
        self._url_async = f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    async def get_session_async(self) -> AsyncGenerator[AsyncSession, None]:
        try:
            air_engine: AsyncEngine = create_async_engine(self._url_async)
            air_async_session = sessionmaker(air_engine, class_=AsyncSession, expire_on_commit=False)
            session: AsyncSession = air_async_session()
            yield session
        finally:
            await session.close()
