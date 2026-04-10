from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.project import ProjectUpdate, ProjectResponse, ProjectListResponse
from backend.services import crud as crud_service
from backend.exceptions import NotFoundError


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectListResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await crud_service.projects.get_projects(db)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(db: AsyncSession = Depends(get_db)):
    return await crud_service.projects.create_project(db)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud_service.projects.get_project(db, project_id)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project_in: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    """Updates the project title and description."""
    
    # 1. Fetch the existing project
    project = await crud_service.projects.get_project(db, project_id)

    # 2. Update the project with new data
    return await crud_service.projects.update_project(db, project, project_in)
