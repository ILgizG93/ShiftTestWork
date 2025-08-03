from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

class ShiftBase(DeclarativeBase):
    ...

class Users(ShiftBase):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    login:  Mapped[str] = mapped_column(String(20), index=True, unique=True)
    password:  Mapped[str] = mapped_column(String(100))
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.id"))
    
    employee: Mapped["Employees"] = relationship(back_populates="user")
    token: Mapped["Tokens"] = relationship("Tokens", back_populates="user")


class Employees(ShiftBase):
    __tablename__ = "employees"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str]
    salary: Mapped[int]
    next_raise_date: Mapped[datetime]
    
    user: Mapped["Users"] = relationship(back_populates="employee", uselist=False)

class Tokens(ShiftBase):
    __tablename__ = "tokens"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(4000), index=True)
    expires_at: Mapped[datetime]
    is_active: Mapped[bool] = mapped_column(nullable=True, default=True)
    
    user: Mapped["Users"] = relationship("Users", back_populates="token")
