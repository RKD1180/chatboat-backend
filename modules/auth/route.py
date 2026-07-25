from fastapi import APIRouter, Depends
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.auth.schema import RegisterRequest, LoginRequest, RefreshRequest
from modules.auth import service as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(data: RegisterRequest):
    result = auth_service.register(data)
    return ApiResponse(message="User registered successfully", data=result, statusCode=201)


@router.post("/login")
async def login(data: LoginRequest):
    result = auth_service.login(data)
    return ApiResponse(message="Login successful", data=result)


@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    result = auth_service.refresh_token(data)
    return ApiResponse(message="Token refreshed successfully", data=result)


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    result = auth_service.get_profile(user)
    return ApiResponse(message="Profile fetched successfully", data=result)


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    return ApiResponse(message="Logged out successfully")
