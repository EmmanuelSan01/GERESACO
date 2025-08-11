from __future__ import annotations

from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.reservations.ReservationsModel import Reservation


class RolEnum(str, Enum):
    user = "user"
    admin = "admin"


class UserBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    email: str = Field(index=True)
    contrasena_hash: str = Field(description="Hash de la contraseña del usuario")
    rol: RolEnum = Field(default=RolEnum.user)


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)

    # Relationships
    reservas: List["Reservation"] = Relationship(back_populates="usuario")


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