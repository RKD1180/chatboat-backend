from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model: Optional[str] = "gemini-flash-latest"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    model: Optional[str]
    userId: str
    createdAt: str
    updatedAt: str
