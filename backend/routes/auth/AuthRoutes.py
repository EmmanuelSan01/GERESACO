from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.auth.controller import AuthController, get_current_user
from app.auth.model import UserRegisterRequest, UserLogin, Token
from backend.core.db import get_session
from backend.controllers.users.UsersController import UsersController

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user
    
    - **nombre**: Full name of the user
    - **email**: Valid email address (must be unique)
    - **contrasena**: Password (minimum 6 characters)
    - **rol**: User role (user/admin, defaults to 'user')
    
    Returns JWT token for immediate authentication
    """
    auth_controller = AuthController(session)
    return auth_controller.register_user(user_data)

@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and get access token
    
    - **email**: User's email address
    - **contrasena**: User's password
    
    Returns JWT token for API access
    """
    auth_controller = AuthController(session)
    return auth_controller.login_user(login_data)

@router.post("/verify-token")
def verify_token(
    current_user = Depends(get_current_user)
):
    """
    Verify if the provided token is valid
    
    Requires Authorization header with Bearer token
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }

@router.get("/me")
def get_current_user_profile(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current authenticated user profile
    
    Requires Authorization header with Bearer token
    """
    users_controller = UsersController(session)
    user = users_controller.get_user(current_user.user_id)
    return user