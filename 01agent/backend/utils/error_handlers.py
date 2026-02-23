import logging
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.procedures import CustomError

logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response format."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        response = {"message": self.message}
        if self.error_code:
            response["error_code"] = self.error_code
        if self.details:
            response["details"] = self.details
        return response

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc}")
    
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        details={"errors": error_details}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )

async def custom_exception_handler(request: Request, exc: CustomError):
    """Handle custom application errors."""
    logger.error(f"Custom error on {request.url}: {exc.message}")
    
    error_response = ErrorResponse(
        message=exc.message,
        error_code="APPLICATION_ERROR"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error on {request.url}: {exc}")
    
    if isinstance(exc, IntegrityError):
        # Handle specific integrity constraint violations
        if "unique constraint" in str(exc).lower():
            error_response = ErrorResponse(
                message="A record with this information already exists",
                error_code="DUPLICATE_RECORD"
            )
            status_code = status.HTTP_409_CONFLICT
        else:
            error_response = ErrorResponse(
                message="Data integrity constraint violated",
                error_code="INTEGRITY_ERROR"
            )
            status_code = status.HTTP_400_BAD_REQUEST
    else:
        error_response = ErrorResponse(
            message="Database operation failed",
            error_code="DATABASE_ERROR"
        )
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP error on {request.url}: {exc.status_code} - {exc.detail}")
    
    error_response = ErrorResponse(
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error occurred",
        error_code="HTTP_ERROR"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        message="An unexpected error occurred",
        error_code="INTERNAL_ERROR"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )