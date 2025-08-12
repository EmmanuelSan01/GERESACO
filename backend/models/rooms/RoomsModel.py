from __future__ import annotations

from enum import Enum
from typing import List, Optional

from sqlmodel import Field, SQLModel
from pydantic import field_validator

class SedeEnum(str, Enum):
    zona_franca = "zona_franca"
    cajasan = "cajasan"
    bogota = "bogota"
    cucuta = "cucuta"
    guatemala = "guatemala"

class RecursoEnum(str, Enum):
    pizarra = "pizarra"
    proyector = "proyector"
    televisor = "televisor"

class RoomBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    sede: SedeEnum
    capacidad: int = Field(gt=0, description="Capacidad máxima de la sala")
    recursos: str = Field(description="Recursos disponibles en la sala")

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
        """Retorna los recursos como un conjunto"""
        return set(r.strip() for r in self.recursos.split(',') if r.strip())

    def has_recurso(self, recurso: str) -> bool:
        """Verifica si la sala tiene un recurso específico"""
        return recurso in self.get_recursos_set()

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