from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.social_media import SocialMedia
from backend.schemas import SocialMediaCreate, SocialMediaUpdate

async def get_project_social_media(db: AsyncSession, project_id: UUID) -> List[SocialMedia]:
    result = await db.execute(
        select(SocialMedia)
        .where(SocialMedia.project_id == project_id)
        .order_by(SocialMedia.created_at.desc())
    )
    return list(result.scalars().all())

async def get_social_media(db: AsyncSession, sm_id: UUID) -> Optional[SocialMedia]:
    result = await db.execute(select(SocialMedia).where(SocialMedia.id == sm_id))
    return result.scalar_one_or_none()

async def create_social_media(db: AsyncSession, sm_in: SocialMediaCreate) -> SocialMedia:
    sm = SocialMedia(**sm_in.model_dump())
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
