from pydantic import BaseModel
from typing import Optional


class PromptCreate(BaseModel):
    projectId: str
    name: str
    content: str
    isDefault: Optional[bool] = False


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    isDefault: Optional[bool] = None


class PromptResponse(BaseModel):
    id: str
    projectId: str
    userId: str
    name: str
    content: str
    isDefault: bool
    createdAt: str
