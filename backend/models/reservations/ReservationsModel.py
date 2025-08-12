from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.users.UsersModel import User
    from models.rooms.RoomsModel import Room

class EstadoReservaEnum(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"

class ReservationBase(SQLModel):
    fecha: dt.date
    hora_inicio: dt.time
    hora_fin: dt.time
    estado: EstadoReservaEnum = Field(default=EstadoReservaEnum.pendiente)

class Reservation(ReservationBase, table=True):
    __tablename__ = "reservation"

    id: Optional[int] = Field(default=None, primary_key=True)

    usuario_id: int = Field(foreign_key="user.id", index=True)
    sala_id: int = Field(foreign_key="room.id", index=True)

    # Relationships
    usuario: "User" = Relationship(back_populates="reservas")
    sala: "Room" = Relationship(back_populates="reservas")

class ReservationCreate(ReservationBase):
    usuario_id: int
    sala_id: int

class ReservationRead(SQLModel):
    id: int
    usuario_id: int
    sala_id: int
    fecha: dt.date
    hora_inicio: dt.time
    hora_fin: dt.time
    estado: EstadoReservaEnum

class ReservationUpdate(SQLModel):
    fecha: Optional[dt.date] = None
    hora_inicio: Optional[dt.time] = None
    hora_fin: Optional[dt.time] = None
    estado: Optional[EstadoReservaEnum] = None