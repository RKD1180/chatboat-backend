from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refreshToken: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    createdAt: str
    updatedAt: str


class TokensResponse(BaseModel):
    accessToken: str
    refreshToken: str


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokensResponse
