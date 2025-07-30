from datetime import datetime
from pydantic import BaseModel

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    username: str = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    full_name: str
    salary: int
    next_raise_date: datetime = None

class User(TunedModel):
    id: int
    username: str
    full_name: str
    salary: int
    next_raise_date: datetime = None
    is_active: bool = None

class UserInDB(User):
    hashed_password: str

class RefreshToken(BaseModel):
    refresh_token: str
