from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from controllers.users.UsersController import UsersController
from core.db import get_session
from models.users.UsersModel import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    return UsersController(session).list_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return UsersController(session).get_user(user_id)

@router.post(
    "/", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    return UsersController(session).create_user(data)

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, data: UserUpdate, session: Session = Depends(get_session)
):
    return UsersController(session).update_user(user_id, data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    UsersController(session).delete_user(user_id)
    return None