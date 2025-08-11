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
        self.session.delete(room)
        self.session.commit()