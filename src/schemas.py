from datetime import datetime
from pydantic import BaseModel

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class TokenCreate(TunedModel):
    user_id: str
    token: str
    expires_at: datetime

class TokenAfterCreate(TokenCreate):
    id: str
    token: str
    expires_at: datetime

class Token(BaseModel):
    token_type: str = "Bearer"
    access_token: str
    refresh_token: str | None = None

class UserBase(BaseModel):
    login: str

class UserAuth(UserBase):
    password: str

class UserCreate(UserBase):
    password: str
    full_name: str
    salary: int
    next_raise_date: datetime = None

class UserSalary(TunedModel):
    user_id: str
    employee_id: str
    salary: int
    next_raise_date: datetime = None

class User(UserBase, UserSalary):
    full_name: str
