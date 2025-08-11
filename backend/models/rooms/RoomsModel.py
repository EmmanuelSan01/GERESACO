from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel
from pydantic import field_validator

if TYPE_CHECKING:
    from models.reservations.ReservationsModel import Reservation


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
    sede: SedeEnum
    capacidad: int = Field(ge=1)
    recursos: str = Field(description="Recursos disponibles en la sala (separados por coma)")

    @field_validator('recursos')
    @classmethod
    def validate_recursos(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Debe especificar al menos un recurso")
        
        # Split by comma and validate each resource
        recursos_list = [r.strip() for r in v.split(',') if r.strip()]
        valid_recursos = {r.value for r in RecursoEnum}
        
        for recurso in recursos_list:
            if recurso not in valid_recursos:
                raise ValueError(f"Recurso inválido: {recurso}. Recursos válidos: {', '.join(valid_recursos)}")
        
        # Remove duplicates and sort for consistency
        unique_recursos = sorted(set(recursos_list))
        return ','.join(unique_recursos)

    def get_recursos_set(self) -> Set[str]:
        # Returns the resources as a set
        return set(r.strip() for r in self.recursos.split(',') if r.strip())

    def has_recurso(self, recurso: str) -> bool:
        # Checks if the room has a specific resource
        return recurso in self.get_recursos_set()


class Room(RoomBase, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    reservas: List["Reservation"] = Relationship(back_populates="sala")


class RoomCreate(RoomBase):
    pass


class RoomRead(SQLModel):
    id: int
    nombre: str
    sede: SedeEnum
    capacidad: int
    recursos: str

    def get_recursos_list(self) -> List[str]:
        # Returns the resources as a list
        return [r.strip() for r in self.recursos.split(',') if r.strip()]


class RoomUpdate(SQLModel):
    nombre: Optional[str] = None
    sede: Optional[SedeEnum] = None
    capacidad: Optional[int] = Field(default=None, ge=1)
    recursos: Optional[str] = Field(default=None, description="Recursos disponibles en la sala (separados por coma)")

    @field_validator('recursos')
    @classmethod
    def validate_recursos(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if not v.strip():
            raise ValueError("Debe especificar al menos un recurso")
        
        # Split by comma and validate each resource
        recursos_list = [r.strip() for r in v.split(',') if r.strip()]
        valid_recursos = {r.value for r in RecursoEnum}
        
        for recurso in recursos_list:
            if recurso not in valid_recursos:
                raise ValueError(f"Recurso inválido: {recurso}. Recursos válidos: {', '.join(valid_recursos)}")
        
        # Remove duplicates and sort for consistency
        unique_recursos = sorted(set(recursos_list))
        return ','.join(unique_recursos)