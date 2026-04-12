from sqlalchemy.exc import SQLAlchemyError


class VidPlanError(Exception):
    """Base exception for all VidPlan errors."""
    pass

class NotFoundError(VidPlanError):
    """Resource not found in DB (project, script, etc.)"""
    pass

class AgentError(VidPlanError):
    """Pydantic AI / LLM call failed."""
    pass

class DatabaseError(VidPlanError):
    """SQLAlchemy operation failed."""
    pass

class ValidationError(VidPlanError):
    """Input/data validation error."""
    pass

class UnauthorizedError(VidPlanError):
    """Unauthorized access attempt."""
    pass


ERROR_MAP = {
    NotFoundError: (404, "NOT_FOUND"),
    ValidationError: (400, "VALIDATION_ERROR"),
    UnauthorizedError: (401, "UNAUTHORIZED"),
    AgentError: (500, "AGENT_ERROR"),
    DatabaseError: (500, "DATABASE_ERROR"),
    SQLAlchemyError: (500, "DATABASE_ERROR"),
}