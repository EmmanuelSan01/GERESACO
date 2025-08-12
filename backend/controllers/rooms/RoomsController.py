from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.models.rooms.RoomsModel import *

class RoomsController:
    def __init__(self, session: Session):
        self.session = session

    def list_rooms(
        self, 
        skip: int = 0, 
        limit: int = 100,
        sede: Optional[SedeEnum] = None,
        recurso: Optional[str] = None
    ) -> List[RoomRead]:
        query = select(Room)
        
        # Filter by sede if provided
        if sede:
            query = query.where(Room.sede == sede)
        
        # Filter by recurso if provided (check if the room has this resource)
        if recurso:
            query = query.where(Room.recursos.contains(recurso))
        
        rooms = self.session.exec(query.offset(skip).limit(limit)).all()
        return [RoomRead.model_validate(r) for r in rooms]

    def get_room(self, room_id: int) -> RoomRead:
        room = self.session.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
            )
        return RoomRead.model_validate(room)

    def get_room_with_reservations(self, room_id: int) -> RoomReadWithReservations:
        """Get room with its reservations using manual join"""
        room = self.session.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
            )
        
        # Manual query to get reservations
        from backend.models.reservations.ReservationsModel import Reservation
        reservations_query = select(Reservation).where(Reservation.sala_id == room_id)
        reservations = self.session.exec(reservations_query).all()
        
        # Convert to dict format
        reservations_dict = [
            {
                "id": r.id,
                "fecha": r.fecha.isoformat(),
                "hora_inicio": r.hora_inicio.strftime("%H:%M:%S"),
                "hora_fin": r.hora_fin.strftime("%H:%M:%S"),
                "estado": r.estado,
                "usuario_id": r.usuario_id
            }
            for r in reservations
        ]
        
        room_data = RoomRead.model_validate(room)
        return RoomReadWithReservations(
            **room_data.model_dump(),
            reservas=reservations_dict
        )

    def create_room(self, data: RoomCreate) -> RoomRead:
        room = Room(**data.model_dump())
        self.session.add(room)
        self.session.commit()
        self.session.refresh(room)
        return RoomRead.model_validate(room)

    def update_room(self, room_id: int, data: RoomUpdate) -> RoomRead:
        room = self.session.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
            )
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(room, k, v)
        self.session.add(room)
        self.session.commit()
        self.session.refresh(room)
        return RoomRead.model_validate(room)

    def delete_room(self, room_id: int) -> None:
        room = self.session.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada"
            )
        
        # Check if room has reservations
        from backend.models.reservations.ReservationsModel import Reservation
        reservations = self.session.exec(
            select(Reservation).where(Reservation.sala_id == room_id)
        ).all()
        
        if reservations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la sala porque tiene reservas asociadas"
            )
        
        self.session.delete(room)
        self.session.commit()
        