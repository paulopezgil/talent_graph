from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.script import ScriptUpdate, ScriptResponse
from backend.services import crud as crud_service

router = APIRouter(prefix="/api/projects", tags=["scripts"])


@router.get("/{project_id}/script", response_model=Optional[ScriptResponse])
async def get_project_script(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud_service.scripts.get_project_script(db, project_id)


@router.post("/{project_id}/script", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_project_script(project_id: UUID, script_in: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    """Creates a new script for the project."""
    return await crud_service.scripts.create_script(db, project_id, script_in.content or "")


@router.put("/{project_id}/script", response_model=ScriptResponse)
async def update_project_script(project_id: UUID, script_in: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    """Updates the existing script for the project. Returns 404 if not found."""
    
    # 1. Fetch the existing script
    script = await crud_service.scripts.get_project_script(db, project_id)

    # 2. If script doesn't exist, raise 404
    return await crud_service.scripts.update_script(db, script, script_in)
