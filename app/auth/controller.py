from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.auth.service import AuthService
from app.auth.model import UserRegisterRequest, UserLogin, Token, TokenData
from backend.controllers.users.UsersController import UsersController
from backend.models.users.UsersModel import UserCreate, User, RolEnum

security = HTTPBearer()

class AuthController:
    def __init__(self, session: Session):
        self.session = session
        self.auth_service = AuthService()
        self.users_controller = UsersController(session)

    def register_user(self, user_data: UserRegisterRequest) -> Token:
        """Register a new user using existing UsersController"""
        # Validate role
        if user_data.rol not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Debe ser 'user' o 'admin'"
            )

        # Hash password and create user using existing UserCreate model
        hashed_password = self.auth_service.get_password_hash(user_data.contrasena)
        
        user_create_data = UserCreate(
            nombre=user_data.nombre,
            email=user_data.email,
            contrasena_hash=hashed_password,
            rol=RolEnum(user_data.rol)
        )

        # Use existing UsersController.create_user method
        created_user = self.users_controller.create_user(user_create_data)

        # Generate access token
        return self._generate_token_for_user(created_user)

    def login_user(self, login_data: UserLogin) -> Token:
        """Authenticate user and return token using existing UsersController"""
        # Use existing get_user_by_email method
        user = self.users_controller.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        # Verify password
        if not self.auth_service.verify_password(login_data.contrasena, user.contrasena_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        # Generate access token
        return self._generate_token_for_user(user)

    def _generate_token_for_user(self, user: User) -> Token:
        """Helper method to generate token for a user"""
        access_token_expires = timedelta(minutes=self.auth_service.access_token_expire_minutes)
        access_token = self.auth_service.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "role": user.rol.value
            },
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.auth_service.get_token_expire_time(),
            user_id=user.id,
            user_role=user.rol.value
        )

    def get_current_user_data(self, token: str) -> TokenData:
        """Get current authenticated user data from token"""
        token_data = self.auth_service.verify_token(token)
        return TokenData(
            email=token_data["email"],
            user_id=token_data["user_id"],
            role=token_data["role"]
        )

# Dependency functions for FastAPI
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Dependency to get current user"""
    auth_service = AuthService()
    token = credentials.credentials
    token_data = auth_service.verify_token(token)
    
    return TokenData(
        email=token_data["email"],
        user_id=token_data["user_id"],
        role=token_data["role"]
    )

def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador"
        )
    return current_user