from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.services.crud.projects import get_projects, create_project, get_project, update_project

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects_route(db: AsyncSession = Depends(get_db)):
    return await get_projects(db)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_route(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await create_project(db, project_in)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_route(project_id: UUID, project_in: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await update_project(db, project, project_in)
