from fastapi import APIRouter, Depends, Query
from config.response import ApiResponse
from middleware.auth import get_current_user
from modules.projects.schema import ProjectCreate, ProjectUpdate
from modules.projects import service as project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/")
async def create_project(data: ProjectCreate, user: dict = Depends(get_current_user)):
    result = project_service.create(data, user["id"])
    return ApiResponse(message="Project created successfully", data=result, statusCode=201)


@router.get("/")
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    result = project_service.list(user["id"], page, limit)
    return ApiResponse(message="Projects fetched successfully", data=result)


@router.get("/{project_id}")
async def get_project(project_id: str, user: dict = Depends(get_current_user)):
    result = project_service.get(project_id, user["id"])
    return ApiResponse(message="Project fetched successfully", data=result)


@router.put("/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate, user: dict = Depends(get_current_user)):
    result = project_service.update(project_id, data, user["id"])
    return ApiResponse(message="Project updated successfully", data=result)


@router.delete("/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(get_current_user)):
    project_service.delete(project_id, user["id"])
    return ApiResponse(message="Project deleted successfully")
