import os
from typing import Any
from fastapi.responses import JSONResponse

from backend.schemas.error import ErrorResponse
from backend.exceptions.classes import (
    NotFoundError,
    AgentError,
    DatabaseError,
    ValidationError,
    UnauthorizedError,
)

async def handle_vidplan_error(exc: Exception, status_code: int = None, error_code: str = None) -> JSONResponse:
    status_code = status_code or 500
    error_code = error_code or exc.__class__.__name__.replace("Error", "").upper()
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error_code=error_code,
            message=exc.message,
        ).model_dump(exclude_none=True),
    )


async def handle_not_found_error(exc: NotFoundError) -> JSONResponse:
    return await handle_vidplan_error(exc, status_code=404, error_code="NOT_FOUND")


async def handle_agent_error(exc: AgentError) -> JSONResponse:
    return await handle_vidplan_error(exc, status_code=500, error_code="AGENT_ERROR")


async def handle_database_error(exc: DatabaseError) -> JSONResponse:
    return await handle_vidplan_error(exc, status_code=500, error_code="DATABASE_ERROR")


async def handle_validation_error(exc: ValidationError) -> JSONResponse:
    return await handle_vidplan_error(exc, status_code=400, error_code="VALIDATION_ERROR")


async def handle_unauthorized_error(exc: UnauthorizedError) -> JSONResponse:
    return await handle_vidplan_error(exc, status_code=401, error_code="UNAUTHORIZED")