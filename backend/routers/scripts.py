from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas import ScriptCreate, ScriptUpdate, ScriptResponse
from backend.services.crud.scripts import get_project_scripts, create_script, get_script, update_script

router = APIRouter(prefix="/api/projects", tags=["scripts"])

@router.get("/{project_id}/scripts", response_model=List[ScriptResponse])
async def get_project_scripts_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_project_scripts(db, project_id)

@router.post("/{project_id}/scripts", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script_route(project_id: UUID, script_in: ScriptCreate, db: AsyncSession = Depends(get_db)):
    if script_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    return await create_script(db, script_in)

@router.put("/{project_id}/scripts/{script_id}", response_model=ScriptResponse)
async def update_script_route(project_id: UUID, script_id: UUID, script_in: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    script = await get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    if script.project_id != project_id:
        raise HTTPException(status_code=400, detail="Script does not belong to this project")
        
    return await update_script(db, script, script_in)
