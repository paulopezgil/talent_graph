from typing import Any, Optional


class VidPlanError(Exception):
    """Base exception for all app errors"""
    pass


class NotFoundError(VidPlanError):
    """Resource not found in DB (project, script, etc.)"""

    def __init__(self, resource: str, identifier: Any):
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} not found: {identifier}"
        super().__init__(message)


class AgentError(VidPlanError):
    """Pydantic AI / LLM call failed"""

    def __init__(self, tool_name: str, message: str):
        message = f"Agent tool '{tool_name}' failed: {message}"
        super().__init__(message)


class DatabaseError(VidPlanError):
    """SQLAlchemy operation failed"""

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        message = f"Database operation '{operation}' failed: {str(original_error)}"
        super().__init__(message)

class ValidationError(VidPlanError):
    """Data validation error"""

    def __init__(self, field: str, reason: str):
        self.field = field
        message = f"Validation error on '{field}': {reason}"
        super().__init__(message)


class UnauthorizedError(VidPlanError):
    """Unauthorized access error"""

    def __init__(self, resource: str):
        self.resource = resource
        message = f"Unauthorized access to {resource}"
        super().__init__(message)