from datetime import date
from typing import List
from fastapi import HTTPException, status
from sqlmodel import select
from backend.models.users.UsersModel import User
from backend.models.rooms.RoomsModel import Room
from backend.models.reservations.ReservationsModel import Reservation, ReservationRead, ReservationReadWithDetails, ReservationCreate, EstadoReservaEnum

class ReservationsController:
    def __init__(self, session):
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
        from datetime import datetime, timedelta
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

    def list_reservations_with_details(self, skip: int = 0, limit: int = 100) -> List[ReservationReadWithDetails]:
        """Get reservations with user and room details using manual joins"""
        reservations = self.session.exec(
            select(Reservation).offset(skip).limit(limit)
        ).all()
        
        result = []
        for reservation in reservations:
            # Get user details
            user = self.session.get(User, reservation.usuario_id)
            user_dict = {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol
            } if user else None
            
            # Get room details
            room = self.session.get(Room, reservation.sala_id)
            room_dict = {
                "id": room.id,
                "nombre": room.nombre,
                "sede": room.sede,
                "capacidad": room.capacidad,
                "recursos": room.recursos
            } if room else None
            
            reservation_data = ReservationRead.model_validate(reservation)
            result.append(ReservationReadWithDetails(
                **reservation_data.model_dump(),
                usuario=user_dict,
                sala=room_dict
            ))
        
        return result

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

    def update_reservation(self, reservation_id: int, data) -> ReservationRead:
        reservation = self.session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate foreign keys if being updated
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

    def get_reservations_by_user(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[ReservationReadWithDetails]:
        """Get all reservations for a specific user"""
        # First check if user exists
        if not self.session.get(User, usuario_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        
        reservations = self.session.exec(
            select(Reservation)
            .where(Reservation.usuario_id == usuario_id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for reservation in reservations:
            # Get user details
            user = self.session.get(User, reservation.usuario_id)
            user_dict = {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol
            } if user else None
            
            # Get room details
            room = self.session.get(Room, reservation.sala_id)
            room_dict = {
                "id": room.id,
                "nombre": room.nombre,
                "sede": room.sede,
                "capacidad": room.capacidad,
                "recursos": room.recursos
            } if room else None
            
            reservation_data = ReservationRead.model_validate(reservation)
            result.append(ReservationReadWithDetails(
                **reservation_data.model_dump(),
                usuario=user_dict,
                sala=room_dict
            ))
        
        return result

    def get_reservations_by_room(self, sala_id: int, skip: int = 0, limit: int = 100) -> List[ReservationReadWithDetails]:
        """Get all reservations for a specific room"""
        # First check if room exists
        if not self.session.get(Room, sala_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala no encontrada",
            )
        
        reservations = self.session.exec(
            select(Reservation)
            .where(Reservation.sala_id == sala_id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for reservation in reservations:
            # Get user details
            user = self.session.get(User, reservation.usuario_id)
            user_dict = {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol
            } if user else None
            
            # Get room details
            room = self.session.get(Room, reservation.sala_id)
            room_dict = {
                "id": room.id,
                "nombre": room.nombre,
                "sede": room.sede,
                "capacidad": room.capacidad,
                "recursos": room.recursos
            } if room else None
            
            reservation_data = ReservationRead.model_validate(reservation)
            result.append(ReservationReadWithDetails(
                **reservation_data.model_dump(),
                usuario=user_dict,
                sala=room_dict
            ))
        
        return result

    def get_reservations_by_date(self, fecha: date, skip: int = 0, limit: int = 100) -> List[ReservationReadWithDetails]:
        """Get all reservations for a specific date"""
        reservations = self.session.exec(
            select(Reservation)
            .where(Reservation.fecha == fecha)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for reservation in reservations:
            # Get user details
            user = self.session.get(User, reservation.usuario_id)
            user_dict = {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol
            } if user else None
            
            # Get room details
            room = self.session.get(Room, reservation.sala_id)
            room_dict = {
                "id": room.id,
                "nombre": room.nombre,
                "sede": room.sede,
                "capacidad": room.capacidad,
                "recursos": room.recursos
            } if room else None
            
            reservation_data = ReservationRead.model_validate(reservation)
            result.append(ReservationReadWithDetails(
                **reservation_data.model_dump(),
                usuario=user_dict,
                sala=room_dict
            ))
        
        return result

    def cancel_reservation(self, reservation_id: int) -> ReservationRead:
        """Cancel a reservation by setting its status to 'cancelada'"""
        reservation = self.session.get(Reservation, reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Reserva no encontrada"
            )
        
        if reservation.estado == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reserva ya está cancelada"
            )
        
        reservation.estado = "cancelada"
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return ReservationRead.model_validate(reservation)