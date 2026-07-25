from fastapi import APIRouter, Depends
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.prompts.schema import PromptCreate, PromptUpdate
from modules.prompts import service as prompt_service

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.post("/")
async def create_prompt(data: PromptCreate, user: dict = Depends(get_current_user)):
    result = prompt_service.create(data, user["id"])
    return ApiResponse(message="Prompt created successfully", data=result, statusCode=201)


@router.get("/")
async def list_prompts(projectId: str, user: dict = Depends(get_current_user)):
    result = prompt_service.list(projectId, user["id"])
    return ApiResponse(message="Prompts fetched successfully", data=result)


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str, user: dict = Depends(get_current_user)):
    result = prompt_service.get(prompt_id, user["id"])
    return ApiResponse(message="Prompt fetched successfully", data=result)


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str, data: PromptUpdate, user: dict = Depends(get_current_user)):
    result = prompt_service.update(prompt_id, data, user["id"])
    return ApiResponse(message="Prompt updated successfully", data=result)


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str, user: dict = Depends(get_current_user)):
    prompt_service.delete(prompt_id, user["id"])
    return ApiResponse(message="Prompt deleted successfully")
