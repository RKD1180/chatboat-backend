from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Prompt:
    id: str
    project_id: str
    user_id: str
    name: str
    content: str
    is_default: bool
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "Prompt":
        return cls(
            id=row[0],
            project_id=row[1],
            user_id=row[2],
            name=row[3],
            content=row[4],
            is_default=row[5],
            created_at=row[6],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "userId": self.user_id,
            "name": self.name,
            "content": self.content,
            "isDefault": self.is_default,
            "createdAt": str(self.created_at),
        }
