from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from backend.models.users.UsersModel import UserCreate, UserRead

class UserLogin(BaseModel):
    email: EmailStr
    contrasena: str

class UserRegisterRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    email: EmailStr
    contrasena: str = Field(min_length=6, description="Contraseña del usuario")
    rol: Optional[str] = Field(default="user", description="Rol del usuario (user/admin)")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    user_role: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None