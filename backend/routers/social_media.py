from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas import SocialMediaCreate, SocialMediaUpdate, SocialMediaResponse
from backend.services.crud.social_media import get_project_social_media, create_social_media, get_social_media, update_social_media

router = APIRouter(prefix="/api/projects", tags=["social-media"])

@router.get("/{project_id}/social-media", response_model=List[SocialMediaResponse])
async def get_project_social_media_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_project_social_media(db, project_id)

@router.post("/{project_id}/social-media", response_model=SocialMediaResponse, status_code=status.HTTP_201_CREATED)
async def create_social_media_route(project_id: UUID, sm_in: SocialMediaCreate, db: AsyncSession = Depends(get_db)):
    if sm_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    return await create_social_media(db, sm_in)

@router.put("/{project_id}/social-media/{sm_id}", response_model=SocialMediaResponse)
async def update_social_media_route(project_id: UUID, sm_id: UUID, sm_in: SocialMediaUpdate, db: AsyncSession = Depends(get_db)):
    sm = await get_social_media(db, sm_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Social Media entry not found")
    if sm.project_id != project_id:
        raise HTTPException(status_code=400, detail="Social Media entry does not belong to this project")
        
    return await update_social_media(db, sm, sm_in)
