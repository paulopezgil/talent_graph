"""
VidPlan AI Exceptions Module.

Exports all exceptions and handlers for use throughout the application.

Example usage:
    from backend.exceptions import VidPlanError
    from backend.exceptions.handlers import handle_vidplan_error
"""

# Base exceptions
from backend.exceptions.classes import (
    VidPlanError,
    NotFoundError,
    AgentError,
    DatabaseError,
    ValidationError,
    UnauthorizedError,
)

# Handlers
from backend.exceptions.handlers import (
    handle_vidplan_error,
    handle_not_found_error,
    handle_agent_error,
    handle_database_error,
    handle_validation_error,
    handle_unauthorized_error,
)

__all__ = [
    # Base HTTP exceptions
    "VidPlanError",
    "NotFoundError",
    "AgentError",
    "DatabaseError",
    "ValidationError",
    "UnauthorizedError",
    # Exception handlers
    "handle_vidplan_error",
    "handle_not_found_error",
    "handle_agent_error",
    "handle_database_error",
    "handle_validation_error",
    "handle_unauthorized_error",
]