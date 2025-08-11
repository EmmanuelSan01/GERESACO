from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.reservations.ReservationsModel import *
from models.users.UsersModel import User
from models.rooms.RoomsModel import Room


class ReservationsController:
    def __init__(self, session: Session):
        self.session = session

    def _ensure_user_and_room(self, usuario_id: int, sala_id: int) -> None:
        if not self.session.get(User, usuario_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        if not self.session.get(Room, sala_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala no encontrada",
            )

    def _validate_time_range(self, hora_inicio, hora_fin) -> None:
        if hora_fin <= hora_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de fin debe ser mayor que la hora de inicio",
            )
        
        # Convert time objects to datetime for duration calculation
        today = datetime.today().date()
        inicio_dt = datetime.combine(today, hora_inicio)
        fin_dt = datetime.combine(today, hora_fin)
        
        duration = fin_dt - inicio_dt
        if duration != timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las reservas deben ser de exactamente 1 hora",
            )

    def list_reservations(self, skip: int = 0, limit: int = 100) -> List[ReservationRead]:
        reservations = self.session.exec(
            select(Reservation).offset(skip).limit(limit)
        ).all()
        return [ReservationRead.model_validate(r) for r in reservations]

    def get_reservation(self, reservation_id: int) -> ReservationRead:
        reservation = self.session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada"
            )
        return ReservationRead.model_validate(reservation)

    def create_reservation(self, data: ReservationCreate) -> ReservationRead:
        self._ensure_user_and_room(data.usuario_id, data.sala_id)
        self._validate_time_range(data.hora_inicio, data.hora_fin)

        reservation = Reservation(**data.model_dump())
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return ReservationRead.model_validate(reservation)

    def update_reservation(
        self, reservation_id: int, data: ReservationUpdate
    ) -> ReservationRead:
        reservation = self.session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate foreign keys if being updated (not typical for PATCH, but covered)
        usuario_id = update_data.get("usuario_id", reservation.usuario_id)
        sala_id = update_data.get("sala_id", reservation.sala_id)
        self._ensure_user_and_room(usuario_id, sala_id)

        # Validate time range if either time is provided
        hora_inicio = update_data.get("hora_inicio", reservation.hora_inicio)
        hora_fin = update_data.get("hora_fin", reservation.hora_fin)
        self._validate_time_range(hora_inicio, hora_fin)

        for k, v in update_data.items():
            setattr(reservation, k, v)

        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return ReservationRead.model_validate(reservation)

    def delete_reservation(self, reservation_id: int) -> None:
        reservation = self.session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada"
            )
        self.session.delete(reservation)
        self.session.commit()