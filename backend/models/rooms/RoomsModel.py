from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel
from pydantic import field_validator

if TYPE_CHECKING:
    from backend.models.reservations.ReservationsModel import Reservation

class SedeEnum(str, Enum):
    zona_franca = "Campus Zona Franca"
    cajasan = "Campus Cajasan"
    bogota = "Campus EAN"
    cucuta = "Campus Medical"
    guatemala = "Campus 502"

class RecursoEnum(str, Enum):
    pizarra = "pizarra"
    proyector = "proyector"
    televisor = "televisor"

class RoomBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    capacidad: int = Field(gt=0, description="Capacidad máxima de la sala")
    descripcion: Optional[str] = None

class Room(RoomBase, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)

    reservas: List["Reservation"] = Relationship(back_populates="sala")

class RoomCreate(RoomBase):
    pass

class RoomRead(SQLModel):
    id: int
    nombre: str
    capacidad: int
    descripcion: Optional[str] = None

class RoomUpdate(SQLModel):
    nombre: Optional[str] = None
    capacidad: Optional[int] = None
    descripcion: Optional[str] = None