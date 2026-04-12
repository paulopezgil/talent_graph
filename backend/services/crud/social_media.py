from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.social_media import SocialMedia
from backend.schemas.social_media import SocialMediaUpdate
from backend.exceptions import NotFoundError


async def get_project_social_media(db: AsyncSession, project_id: UUID) -> Optional[SocialMedia]:
    result = await db.execute(select(SocialMedia).where(SocialMedia.project_id == project_id))
    social_media = result.scalar_one_or_none()
    
    if social_media is None:
        raise NotFoundError(f"Social media content for project with id {project_id} not found")

    return social_media

async def create_social_media(db: AsyncSession, project_id: UUID, sm_in: SocialMediaUpdate) -> SocialMedia:
    sm = SocialMedia(project_id=project_id, **sm_in.model_dump(exclude_unset=True))
    db.add(sm)
    await db.commit()
    await db.refresh(sm)
    return sm

async def update_social_media(db: AsyncSession, sm: SocialMedia, sm_in: SocialMediaUpdate) -> SocialMedia:
    update_data = sm_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sm, field, value)
    await db.commit()
    await db.refresh(sm)
    return sm
