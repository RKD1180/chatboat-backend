from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TrainingData:
    id: str
    project_id: str
    user_id: str
    content: str
    type: str
    file_name: Optional[str]
    metadata: Optional[dict]
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "TrainingData":
        return cls(
            id=row[0],
            project_id=row[1],
            user_id=row[2],
            content=row[3],
            type=row[4],
            file_name=row[5],
            metadata=row[6],
            created_at=row[7],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "userId": self.user_id,
            "content": self.content,
            "type": self.type,
            "fileName": self.file_name,
            "metadata": self.metadata,
            "createdAt": str(self.created_at),
        }
