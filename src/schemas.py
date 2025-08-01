from datetime import datetime
from pydantic import BaseModel

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    login: str = None

class UserBase(BaseModel):
    login: str

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

class UserInDB(User):
    hashed_password: str

class RefreshToken(BaseModel):
    refresh_token: str
