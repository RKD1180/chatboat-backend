from fastapi import APIRouter, Depends
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.settings.schema import SettingsUpdate, ProfileUpdate
from modules.settings import service as settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/")
async def get_settings(user: dict = Depends(get_current_user)):
    result = settings_service.get_settings(user["id"])
    return ApiResponse(message="Settings fetched successfully", data=result)


@router.put("/")
async def update_settings(data: SettingsUpdate, user: dict = Depends(get_current_user)):
    result = settings_service.update_settings(data, user["id"])
    return ApiResponse(message="Settings updated successfully", data=result)


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    result = settings_service.get_profile(user["id"])
    return ApiResponse(message="Profile fetched successfully", data=result)


@router.put("/profile")
async def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    result = settings_service.update_profile(data, user["id"])
    return ApiResponse(message="Profile updated successfully", data=result)
