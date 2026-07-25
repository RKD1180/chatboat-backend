from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Project:
    id: str
    name: str
    description: Optional[str]
    model: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Project":
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            model=row[3],
            user_id=row[4],
            created_at=row[5],
            updated_at=row[6] if len(row) > 6 else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "userId": self.user_id,
            "createdAt": str(self.created_at),
            "updatedAt": str(self.updated_at) if self.updated_at else str(self.created_at),
        }
