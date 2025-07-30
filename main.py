from fastapi import FastAPI

from config.settings import Settings
from loggers import init_logger
from src.routers import router

app = FastAPI()
app.include_router(router)
logger = init_logger("app")
settings: Settings = Settings()
