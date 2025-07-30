import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .database import DataBaseServer

load_dotenv()

class Settings(BaseSettings):
    secret_key: str = os.environ.get("SECRET_KEY")
    algorithm: str = os.environ.get("ALGORITHM")
    access_token_expire_time: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 14)

    database: DataBaseServer = DataBaseServer(
        os.environ.get("DB_HOST"), 
        os.environ.get("DB_PORT"), 
        os.environ.get("DB_USER"), 
        os.environ.get("DB_PASS"), 
        os.environ.get("DB_NAME")
    )
