from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.conversation_context import ConversationContext
from backend.schemas.conversation_context import ConversationContextUpdate


async def get_conversation_context(db: AsyncSession, project_id: UUID) -> Optional[ConversationContext]:
    """Get conversation context for a project. Returns None if not found."""
    result = await db.execute(
        select(ConversationContext).where(ConversationContext.project_id == project_id)
    )
    return result.scalar_one_or_none()


async def update_conversation_context(
    db: AsyncSession,
    conversation_context: ConversationContext,
    context_in: ConversationContextUpdate,
) -> ConversationContext:
    """Update conversation context fields."""
    update_data = context_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation_context, field, value)
    await db.commit()
    await db.refresh(conversation_context)
    return conversation_context