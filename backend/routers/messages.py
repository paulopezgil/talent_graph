from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.message import Message
from backend.schemas import MessageResponse

router = APIRouter(prefix="/api/projects", tags=["messages"])

@router.get("/{project_id}/messages", response_model=List[MessageResponse])
async def get_project_messages(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())
