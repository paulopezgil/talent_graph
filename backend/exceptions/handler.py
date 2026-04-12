import logging
from fastapi.responses import JSONResponse
from backend.exceptions.classes import ERROR_MAP, VidPlanError


logger = logging.getLogger(__name__)


def _get_error_details(exc: VidPlanError):
    """Maps exceptions to status codes and error codes."""

    # Get the error message
    error_message = str(exc)

    # Check if the exception matches any known error types
    for error_type, (status_code, error_code) in ERROR_MAP.items():
        if isinstance(exc, error_type):
            return status_code, error_code, error_message
        
    # Default to 500 for unhandled exceptions
    return 500, exc.__class__.__name__.upper(), error_message

def _log_exception(exc: VidPlanError, status_code: int):
    """Logs exceptions with appropriate severity based on status code."""
    if status_code >= 500:
        logger.error(f"ERROR:    Internal error of type {exc.__class__.__name__}: {exc}", exc_info=True)
    elif status_code >= 400:
        logger.warning(f"WARNING:  Client error of type {exc.__class__.__name__}: {exc}")
    else:
        logger.info(f"INFO:     Handled error of type {exc.__class__.__name__}: {exc}")

async def handle_vidplan_error(exc: VidPlanError) -> JSONResponse:
    """Centralized error handler for VidPlan exceptions."""

    # Get the error details (status code, error code, message)
    status_code, error_code, error_message = _get_error_details(exc)

    # Log the error with appropriate severity
    _log_exception(exc, status_code)
    
    return JSONResponse(
        status_code=status_code,
        content = {
            "error_code": error_code,
            "message": error_message,
        }
    )