from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class File:
    id: str
    project_id: str
    user_id: str
    name: str
    original_name: str
    mime_type: Optional[str]
    size: Optional[int]
    path: str
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "File":
        return cls(
            id=row[0],
            project_id=row[1],
            user_id=row[2],
            name=row[3],
            original_name=row[4],
            mime_type=row[5],
            size=row[6],
            path=row[7],
            created_at=row[8],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "userId": self.user_id,
            "name": self.name,
            "originalName": self.original_name,
            "mimeType": self.mime_type,
            "size": self.size,
            "path": self.path,
            "createdAt": str(self.created_at),
        }
