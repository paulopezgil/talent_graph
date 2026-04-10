from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.schemas.social_media import SocialMediaUpdate, SocialMediaResponse
from backend.services import crud as crud_service

router = APIRouter(prefix="/api/projects", tags=["social-media"])


@router.get("/{project_id}/social-media", response_model=Optional[SocialMediaResponse])
async def get_project_social_media(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud_service.social_media.get_project_social_media(db, project_id)


@router.post("/{project_id}/social-media", response_model=SocialMediaResponse, status_code=status.HTTP_201_CREATED)
async def create_project_social_media(project_id: UUID, sm_in: SocialMediaUpdate, db: AsyncSession = Depends(get_db)):
    """Creates new social media content for the project."""
    return await crud_service.social_media.create_social_media(db, project_id, sm_in)


@router.put("/{project_id}/social-media", response_model=SocialMediaResponse)
async def update_project_social_media(project_id: UUID, sm_in: SocialMediaUpdate, db: AsyncSession = Depends(get_db)):
    """Updates existing social media content for the project."""
    
    # 1. Fetch the existing social media content
    social_media = await crud_service.social_media.get_project_social_media(db, project_id)

    # 2. If social media content doesn't exist, raise 404
    return await crud_service.social_media.update_social_media(db, social_media, sm_in)
