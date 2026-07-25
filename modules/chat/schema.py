from pydantic import BaseModel
from typing import Optional


class CreateConversationRequest(BaseModel):
    projectId: str
    title: Optional[str] = "New Chat"


class SendMessageRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: str
    projectId: str
    userId: str
    title: str
    createdAt: str
    updatedAt: str


class MessageResponse(BaseModel):
    id: str
    conversationId: str
    role: str
    content: str
    createdAt: str


class SendMessageResponse(BaseModel):
    userMessage: dict
    assistantMessage: dict
