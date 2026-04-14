from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: Any = None):
        return {"success": True, "data": data, "error": None}

    @classmethod
    def fail(cls, error: str):
        return {"success": False, "data": None, "error": error}
