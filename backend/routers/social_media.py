from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.social_media import SocialMedia
from backend.schemas import SocialMediaCreate, SocialMediaUpdate, SocialMediaResponse

router = APIRouter(prefix="/api/projects", tags=["social-media"])


@router.get("/{project_id}/social-media", response_model=List[SocialMediaResponse])
async def get_project_social_media(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SocialMedia)
        .where(SocialMedia.project_id == project_id)
        .order_by(SocialMedia.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{project_id}/social-media", response_model=SocialMediaResponse, status_code=status.HTTP_201_CREATED)
async def create_social_media(project_id: UUID, sm_in: SocialMediaCreate, db: AsyncSession = Depends(get_db)):
    if sm_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
        
    sm = SocialMedia(**sm_in.model_dump())
    db.add(sm)
    await db.commit()
    await db.refresh(sm)
    return sm


@router.put("/{project_id}/social-media/{sm_id}", response_model=SocialMediaResponse)
async def update_social_media(project_id: UUID, sm_id: UUID, sm_in: SocialMediaUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SocialMedia).where(SocialMedia.id == sm_id))
    sm = result.scalar_one_or_none()
    if not sm:
        raise HTTPException(status_code=404, detail="Social Media entry not found")
        
    if sm.project_id != project_id:
        raise HTTPException(status_code=400, detail="Social Media entry does not belong to this project")
        
    update_data = sm_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sm, field, value)
        
    await db.commit()
    await db.refresh(sm)
    return sm
