from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.routers import projects, messages, scripts, social_media
from backend.core.database import engine
from backend.models import Base
from backend.exceptions.handlers import (
    handle_vidplan_error, handle_not_found_error, handle_agent_error, 
    handle_database_error, handle_validation_error, handle_unauthorized_error,
)
from backend.exceptions.classes import (
    NotFoundError, AgentError, DatabaseError,
    ValidationError, UnauthorizedError,
)

@asynccontextmanager
async def lifespan(application: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Vidplan AI", version="0.1.0", lifespan=lifespan)

# Data Routes
app.include_router(projects.router)
app.include_router(messages.router)
app.include_router(scripts.router)
app.include_router(social_media.router)

# Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc):
    return await handle_not_found_error(exc)

@app.exception_handler(AgentError)
async def agent_exception_handler(request, exc):
    return await handle_agent_error(exc)

@app.exception_handler(DatabaseError)
async def database_exception_handler(request, exc):
    return await handle_database_error(exc)

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Convert SQLAlchemy exceptions into our custom DatabaseError and handle it."""
    db_error = DatabaseError(operation="unknown", original_error=exc)
    return await handle_database_error(db_error)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return await handle_validation_error(exc)

@app.exception_handler(UnauthorizedError)
async def unauthorized_exception_handler(request, exc):
    return await handle_unauthorized_error(exc)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return await handle_vidplan_error(exc)