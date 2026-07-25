from pydantic import BaseModel
from typing import Optional


class TextRequest(BaseModel):
    projectId: str
    content: str


class TrainingResponse(BaseModel):
    id: str
    projectId: str
    userId: str
    content: str
    type: str
    fileName: Optional[str]
    metadata: Optional[dict]
    createdAt: str
