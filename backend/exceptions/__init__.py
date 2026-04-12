"""
VidPlan AI Exceptions Module.

Exports all exceptions and handlers for use throughout the application.

Example usage:
    from backend.exceptions import VidPlanError
    from backend.exceptions import handle_vidplan_error
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

# Handler
from backend.exceptions.handler import handle_vidplan_error

__all__ = (

    # Base HTTP exceptions
    "VidPlanError",
    "NotFoundError",
    "AgentError",
    "DatabaseError",
    "ValidationError",
    "UnauthorizedError",

    # Exception handler
    "handle_vidplan_error",
)