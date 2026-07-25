from pydantic import BaseModel
from typing import Any, Optional


class ApiResponse(BaseModel):
    message: str
    data: Any = None
    statusCode: int = 200


class PaginatedData(BaseModel):
    data: list
    total: int
    page: int
    limit: int
    totalPages: int
