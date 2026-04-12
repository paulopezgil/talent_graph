from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from sqlalchemy import text
import logging

from backend.routers import projects, messages, scripts, social_media
from backend.core.database import engine
from backend.models import Base
from backend.exceptions import VidPlanError, handle_vidplan_error



# Set up logging
logger = logging.getLogger(__name__)


# FastAPI app with lifespan to handle DB initialization and cleanup
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


# Global Exception Handler
@app.exception_handler(VidPlanError)
async def global_exception_handler(request: Request, exc: VidPlanError) -> JSONResponse:
    return await handle_vidplan_error(exc)