from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.script import Script
from backend.schemas import ScriptCreate, ScriptUpdate, ScriptResponse

router = APIRouter(prefix="/api/projects", tags=["scripts"])


@router.get("/{project_id}/scripts", response_model=List[ScriptResponse])
async def get_project_scripts(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Script).where(Script.project_id == project_id).order_by(Script.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{project_id}/scripts", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(project_id: UUID, script_in: ScriptCreate, db: AsyncSession = Depends(get_db)):
    if script_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
        
    script = Script(**script_in.model_dump())
    db.add(script)
    await db.commit()
    await db.refresh(script)
    return script


@router.put("/{project_id}/scripts/{script_id}", response_model=ScriptResponse)
async def update_script(project_id: UUID, script_id: UUID, script_in: ScriptUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    if script.project_id != project_id:
        raise HTTPException(status_code=400, detail="Script does not belong to this project")
        
    update_data = script_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(script, field, value)
        
    await db.commit()
    await db.refresh(script)
    return script
