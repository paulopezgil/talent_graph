from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.chat import ChatInput, ChatResponse
from backend.services import crud as crud_service
from backend.services.conversation import generate_chat_response


router = APIRouter(prefix="/projects", tags=["chat"])


@router.post("/{project_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    project_id: UUID,
    request: ChatInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Sends a chat message and gets an AI response.
    Does not persist messages - they are session-based only.
    Updates conversation context (summary) for AI memory.
    Includes session-based message history for conversation continuity.
    """
    # First verify project exists
    await crud_service.projects.get_project(db, project_id)

    # Generate response (reads conversation context, includes history, updates summary, returns response)
    return await generate_chat_response(
        db,
        project_id,
        request.content,
        history=request.history,
    )