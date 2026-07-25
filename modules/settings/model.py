from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Settings:
    id: str
    user_id: str
    theme: str
    language: str
    notifications: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Settings":
        return cls(
            id=row[0],
            user_id=row[1],
            theme=row[2],
            language=row[3],
            notifications=row[4],
            created_at=row[5],
            updated_at=row[6] if len(row) > 6 else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "theme": self.theme,
            "language": self.language,
            "notifications": self.notifications,
            "createdAt": str(self.created_at),
            "updatedAt": str(self.updated_at) if self.updated_at else str(self.created_at),
        }
