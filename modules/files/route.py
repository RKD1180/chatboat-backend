from fastapi import APIRouter, Depends, UploadFile, File as UploadFileObj, Form
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.files import service as file_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    projectId: str = Form(...),
    file: UploadFile = UploadFileObj(...),
    user: dict = Depends(get_current_user),
):
    result = await file_service.upload(projectId, file, user["id"])
    return ApiResponse(message="File uploaded successfully", data=result, statusCode=201)


@router.get("/")
async def list_files(projectId: str, user: dict = Depends(get_current_user)):
    result = file_service.list(projectId, user["id"])
    return ApiResponse(message="Files fetched successfully", data=result)


@router.delete("/{file_id}")
async def delete_file(file_id: str, user: dict = Depends(get_current_user)):
    file_service.delete(file_id, user["id"])
    return ApiResponse(message="File deleted successfully")
