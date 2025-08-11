from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from backend.controllers.reservations.ReservationsController import ReservationsController
from backend.core.db import get_session
from backend.models.reservations.ReservationsModel import *

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=List[ReservationRead])
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    return ReservationsController(session).list_reservations(skip=skip, limit=limit)


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: int, session: Session = Depends(get_session)):
    return ReservationsController(session).get_reservation(reservation_id)


@router.post(
    "/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED
)
def create_reservation(
    data: ReservationCreate, session: Session = Depends(get_session)
):
    return ReservationsController(session).create_reservation(data)


@router.patch("/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    reservation_id: int, data: ReservationUpdate, session: Session = Depends(get_session)
):
    return ReservationsController(session).update_reservation(reservation_id, data)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, session: Session = Depends(get_session)):
    ReservationsController(session).delete_reservation(reservation_id)
    return None
