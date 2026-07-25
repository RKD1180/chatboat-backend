from pydantic import BaseModel
from typing import Optional


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications: Optional[bool] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class SettingsResponse(BaseModel):
    id: str
    userId: str
    theme: str
    language: str
    notifications: bool
    createdAt: str
    updatedAt: str


class ProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    createdAt: str
