from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.routers import agent, projects, messages, scripts, social_media
from backend.services.pgvector_service.client import db_client
from backend.services.pgvector_service.ensure_table import ensure_table


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Depending on current state, the db_client / ensure_table
    # might need restructuring later to fit the asyncpg engine.
    try:
        await db_client.connect()
        await ensure_table()
    except Exception as e:
        print(f"Warning: db_client connection failed during startup: {e}")
    yield
    try:
        await db_client.close()
    except Exception:
        pass


app = FastAPI(title="Vidplan AI", version="0.1.0", lifespan=lifespan)

# Agent Routes
app.include_router(agent.router)

# Data Routes
app.include_router(projects.router)
app.include_router(messages.router)
app.include_router(scripts.router)
app.include_router(social_media.router)
