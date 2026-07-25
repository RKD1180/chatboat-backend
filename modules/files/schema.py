from pydantic import BaseModel
from typing import Optional


class FileResponse(BaseModel):
    id: str
    projectId: str
    userId: str
    name: str
    originalName: str
    mimeType: Optional[str]
    size: Optional[int]
    path: str
    createdAt: str
