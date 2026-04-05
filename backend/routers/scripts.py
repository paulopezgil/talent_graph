from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.schemas.script import ScriptCreate, ScriptUpdate, ScriptResponse
from backend.services.crud.scripts import get_project_script, create_script, update_script

router = APIRouter(prefix="/api/projects", tags=["scripts"])

@router.get("/{project_id}/script", response_model=Optional[ScriptResponse])
async def get_project_script_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_project_script(db, project_id)

@router.put("/{project_id}/script", response_model=ScriptResponse)
async def update_or_create_script_route(project_id: UUID, script_in: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    script = await get_project_script(db, project_id)
    if not script:
        # Create it (Upsert)
        create_data = ScriptCreate(project_id=project_id, content=script_in.content or "")
        return await create_script(db, create_data)
        
    return await update_script(db, script, script_in)
