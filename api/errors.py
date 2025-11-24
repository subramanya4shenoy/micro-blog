from typing import Optional
from pydantic import BaseModel


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class AppError(Exception):
    """
    Our own application level error handler.
    we will through this from routes/services instead of raw HTTP EXCEPTION
    """
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}