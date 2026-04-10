from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.message import MessageInput, MessageResponse
from backend.services import crud as crud_service
from backend.services import conversation as conversation_service

router = APIRouter(prefix="/api/projects", tags=["messages"])



@router.get("/{project_id}/messages", response_model=List[MessageResponse])
async def get_project_messages(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Returns the entire conversation history for the project."""
    return await crud_service.messages.get_project_messages(db, project_id)

@router.post("/{project_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_project_message(project_id: UUID, request: MessageInput, db: AsyncSession = Depends(get_db)):
    """
    Adds a new user message, invokes the AI agent, and returns the AI's response.
    The agent execution is a side-effect of posting a message.
    """
    return await conversation_service.get_agent_response(db, project_id, request.content)

@router.put("/{project_id}/messages/last", response_model=MessageResponse)
async def update_last_message(project_id: UUID, request: MessageInput, db: AsyncSession = Depends(get_db)):
    """Deletes the last exchange, then creates a new exchange with the provided content."""

    # 1. Delete last exchange (last user + assistant messages)
    await conversation_service.delete_last_exchange(db, project_id)
    
    # 2. Create new exchange with updated content
    return await conversation_service.get_agent_response(db, project_id, request.content)
