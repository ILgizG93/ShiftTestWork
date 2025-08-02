from fastapi import FastAPI

from config.settings import Settings
from src.routers import router

app = FastAPI()
app.include_router(router)
settings: Settings = Settings()
