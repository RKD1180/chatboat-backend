from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Conversation:
    id: str
    project_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Conversation":
        return cls(
            id=row[0],
            project_id=row[1],
            user_id=row[2],
            title=row[3],
            created_at=row[4],
            updated_at=row[5] if len(row) > 5 else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "userId": self.user_id,
            "title": self.title,
            "createdAt": str(self.created_at),
            "updatedAt": str(self.updated_at) if self.updated_at else str(self.created_at),
        }


@dataclass
class Message:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "Message":
        return cls(
            id=row[0],
            conversation_id=row[1],
            role=row[2],
            content=row[3],
            created_at=row[4],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversationId": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "createdAt": str(self.created_at),
        }
