from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas import MessageResponse
from backend.services.crud.messages import get_project_messages

router = APIRouter(prefix="/api/projects", tags=["messages"])

@router.get("/{project_id}/messages", response_model=List[MessageResponse])
async def get_project_messages_route(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_project_messages(db, project_id)
