from fastapi import APIRouter, Depends, UploadFile, File, Form
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.training.schema import TextRequest
from modules.training import service as training_service

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("/text")
async def add_text(data: TextRequest, user: dict = Depends(get_current_user)):
    result = await training_service.add_text(data, user["id"])
    return ApiResponse(message="Training text added successfully", data=result, statusCode=201)


@router.post("/pdf")
async def add_pdf(
    projectId: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    result = await training_service.add_pdf(projectId, file, user["id"])
    return ApiResponse(message="PDF uploaded successfully", data=result, statusCode=201)


@router.get("/")
async def list_training(projectId: str, user: dict = Depends(get_current_user)):
    result = training_service.list(projectId, user["id"])
    return ApiResponse(message="Training data fetched successfully", data=result)


@router.delete("/{training_id}")
async def delete_training(training_id: str, user: dict = Depends(get_current_user)):
    training_service.delete(training_id, user["id"])
    return ApiResponse(message="Training data deleted successfully")
