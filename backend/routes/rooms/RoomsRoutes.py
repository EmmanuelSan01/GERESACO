from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from backend.controllers.rooms.RoomsController import RoomsController
from backend.core.db import get_session
from backend.models.rooms.RoomsModel import RoomCreate, RoomRead, RoomUpdate, SedeEnum
from app.auth.controller import get_current_user, require_admin
from app.auth.model import TokenData

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[RoomRead])
def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sede: Optional[SedeEnum] = Query(None, description="Filtrar por sede"),
    recurso: Optional[str] = Query(None, description="Filtrar por recurso específico"),
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)  # For authentication
):
    return RoomsController(session).list_rooms(
        skip=skip, limit=limit, sede=sede, recurso=recurso
    )


@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, session: Session = Depends(get_session)):
    return RoomsController(session).get_room(room_id)


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(
    data: RoomCreate, 
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)  # Only admin
):
    return RoomsController(session).create_room(data)


@router.patch("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int, 
    data: RoomUpdate, 
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)  # Only admin
):
    return RoomsController(session).update_room(room_id, data)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int, 
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(require_admin)  # Only admin
):
    RoomsController(session).delete_room(room_id)
    return None