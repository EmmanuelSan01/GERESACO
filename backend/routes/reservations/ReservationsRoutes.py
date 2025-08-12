from typing import List
from datetime import date

from fastapi import APIRouter, Depends, Query, status, Path
from sqlmodel import Session

from backend.controllers.reservations.ReservationsController import ReservationsController
from backend.core.db import get_session
from backend.models.reservations.ReservationsModel import *

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate, session: Session = Depends(get_session)
):
    """Create a new reservation"""
    return ReservationsController(session).create_reservation(data)


@router.get("/", response_model=List[ReservationReadWithDetails])
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Get all reservations with user and room details"""
    return ReservationsController(session).list_reservations_with_details(skip=skip, limit=limit)


@router.get("/room/{room_id}", response_model=List[ReservationReadWithDetails])
def get_reservations_by_room(
    room_id: int = Path(..., description="ID of the room"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all reservations for a specific room"""
    return ReservationsController(session).get_reservations_by_room(room_id, skip=skip, limit=limit)


@router.get("/date/{reservation_date}", response_model=List[ReservationReadWithDetails])
def get_reservations_by_date(
    reservation_date: date = Path(..., description="Date in YYYY-MM-DD format"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all reservations for a specific date"""
    return ReservationsController(session).get_reservations_by_date(reservation_date, skip=skip, limit=limit)


@router.delete("/{reservation_id}", response_model=ReservationRead)
def cancel_reservation(
    reservation_id: int = Path(..., description="ID of the reservation to cancel"),
    session: Session = Depends(get_session)
):
    """Cancel a reservation (sets status to 'cancelada')"""
    return ReservationsController(session).cancel_reservation(reservation_id)


# Keep existing endpoints for backward compatibility
@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: int, session: Session = Depends(get_session)):
    """Get a specific reservation by ID"""
    return ReservationsController(session).get_reservation(reservation_id)


@router.patch("/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    reservation_id: int, data: ReservationUpdate, session: Session = Depends(get_session)
):
    """Update a reservation"""
    return ReservationsController(session).update_reservation(reservation_id, data)