from __future__ import annotations

from enum import Enum
from typing import List, Optional

from sqlmodel import Field, SQLModel

class SedeEnum(str, Enum):
    zona_franca = "zona_franca"
    cajasan = "cajasan"
    bogota = "bogota"
    cucuta = "cucuta"
    guatemala = "guatemala"

class RoomBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    sede: SedeEnum
    capacidad: int = Field(gt=0, description="Capacidad máxima de la sala")
    recursos: str = Field(description="Recursos disponibles en la sala")

class Room(RoomBase, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)

class RoomCreate(RoomBase):
    pass

class RoomRead(SQLModel):
    id: int
    nombre: str
    sede: SedeEnum
    capacidad: int
    recursos: str

class RoomUpdate(SQLModel):
    nombre: Optional[str] = None
    sede: Optional[SedeEnum] = None
    capacidad: Optional[int] = None
    recursos: Optional[str] = None

# Extended read model that includes reservations when needed
class RoomReadWithReservations(RoomRead):
    reservas: Optional[List[dict]] = None