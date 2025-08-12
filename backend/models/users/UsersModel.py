from __future__ import annotations

from enum import Enum
from typing import List, Optional

from sqlmodel import Field, SQLModel

class RolEnum(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    email: str
    contrasena_hash: str = Field(description="Hash de la contraseña del usuario")
    rol: RolEnum = Field(default=RolEnum.user)

class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)

class UserCreate(UserBase):
    pass

class UserRead(SQLModel):
    id: int
    nombre: str
    email: str
    rol: RolEnum

class UserUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    contrasena_hash: Optional[str] = None
    rol: Optional[RolEnum] = None

# Extended read model that includes reservations when needed
class UserReadWithReservations(UserRead):
    reservas: Optional[List[dict]] = None