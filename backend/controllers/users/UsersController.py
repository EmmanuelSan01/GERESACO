from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.models.users.UsersModel import *

class UsersController:
    def __init__(self, session: Session):
        self.session = session

    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserRead]:
        users = self.session.exec(select(User).offset(skip).limit(limit)).all()
        return [UserRead.model_validate(u) for u in users]

    def get_user(self, user_id: int) -> UserRead:
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return UserRead.model_validate(user)

    def get_user_with_reservations(self, user_id: int) -> UserReadWithReservations:
        """Get user with their reservations using manual join"""
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        
        # Manual query to get reservations
        from backend.models.reservations.ReservationsModel import Reservation
        reservations_query = select(Reservation).where(Reservation.usuario_id == user_id)
        reservations = self.session.exec(reservations_query).all()
        
        # Convert to dict format
        reservations_dict = [
            {
                "id": r.id,
                "fecha": r.fecha.isoformat(),
                "hora_inicio": r.hora_inicio.strftime("%H:%M:%S"),
                "hora_fin": r.hora_fin.strftime("%H:%M:%S"),
                "estado": r.estado,
                "sala_id": r.sala_id
            }
            for r in reservations
        ]
        
        user_data = UserRead.model_validate(user)
        return UserReadWithReservations(
            **user_data.model_dump(),
            reservas=reservations_dict
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.session.exec(stmt).first()

    def create_user(self, data: UserCreate) -> UserRead:
        # Enforce unique email
        if self.get_user_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado"
            )
        user = User(**data.model_dump())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserRead.model_validate(user)

    def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        # If email is changing, ensure uniqueness
        if data.email and data.email != user.email:
            if self.get_user_by_email(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El email ya está registrado",
                )

        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(user, k, v)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserRead.model_validate(user)

    def delete_user(self, user_id: int) -> None:
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        
        # Check if user has reservations
        from backend.models.reservations.ReservationsModel import Reservation
        reservations = self.session.exec(
            select(Reservation).where(Reservation.usuario_id == user_id)
        ).all()
        
        if reservations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el usuario porque tiene reservas asociadas"
            )
        
        self.session.delete(user)
        self.session.commit()