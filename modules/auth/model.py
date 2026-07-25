from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    id: str
    email: str
    display_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            id=row[0],
            email=row[1],
            display_name=row[2],
            created_at=row[3],
            updated_at=row[4] if len(row) > 4 else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.display_name or self.email.split("@")[0],
            "createdAt": str(self.created_at),
            "updatedAt": str(self.updated_at) if self.updated_at else str(self.created_at),
        }
