from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.schemas.social_media import SocialMediaCreate, SocialMediaUpdate, SocialMediaResponse
from backend.services.crud.social_media import get_project_social_media, create_social_media, update_social_media

router = APIRouter(prefix="/api/projects", tags=["social-media"])

@router.get("/{project_id}/social-media", response_model=Optional[SocialMediaResponse])
async def get_project_social_media_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_project_social_media(db, project_id)

@router.put("/{project_id}/social-media", response_model=SocialMediaResponse)
async def update_or_create_social_media_route(project_id: UUID, sm_in: SocialMediaUpdate, db: AsyncSession = Depends(get_db)):
    sm = await get_project_social_media(db, project_id)
    if not sm:
        # Create it (Upsert)
        create_data = SocialMediaCreate(
            project_id=project_id,
            **sm_in.model_dump(exclude_unset=True)
        )
        return await create_social_media(db, create_data)
        
    return await update_social_media(db, sm, sm_in)
