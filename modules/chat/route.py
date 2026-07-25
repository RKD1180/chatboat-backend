from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.chat.schema import CreateConversationRequest, SendMessageRequest
from modules.chat import service as chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None


@router.post("/conversations")
async def create_conversation(data: CreateConversationRequest, user: dict = Depends(get_current_user)):
    result = chat_service.create_conversation(data, user["id"])
    return ApiResponse(message="Conversation created successfully", data=result, statusCode=201)


@router.get("/conversations")
async def get_conversations(projectId: Optional[str] = None, user: dict = Depends(get_current_user)):
    result = chat_service.get_conversations(user["id"], projectId)
    return ApiResponse(message="Conversations fetched successfully", data=result)


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    data: UpdateConversationRequest,
    user: dict = Depends(get_current_user),
):
    result = chat_service.update_conversation(conversation_id, user["id"], data.title)
    return ApiResponse(message="Conversation updated successfully", data=result)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    chat_service.delete_conversation(conversation_id, user["id"])
    return ApiResponse(message="Conversation deleted successfully")


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: SendMessageRequest,
    user: dict = Depends(get_current_user),
):
    result = await chat_service.send_message(conversation_id, data, user["id"])
    return ApiResponse(message="Message sent successfully", data=result)


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, user: dict = Depends(get_current_user)):
    result = chat_service.get_messages(conversation_id, user["id"])
    return ApiResponse(message="Messages fetched successfully", data=result)
