from typing import List, Any
from app.schemas.common import BaseSchema

class ErrorDetail(BaseSchema):
    field: str = ""
    message: str = ""

class ErrorResponse(BaseSchema):
    status: str = "error"
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"
    details: List[Any] = []
