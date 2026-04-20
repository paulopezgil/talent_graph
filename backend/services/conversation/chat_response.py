from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.crud.conversation_context import get_conversation_context, update_conversation_context
from backend.schemas.conversation_context import ConversationContextUpdate
from backend.services.agent import generate_agent_response


async def generate_chat_response(
    db: AsyncSession,
    project_id: UUID,
    content: str,
    history: Optional[List[dict]] = None,
) -> dict:
    """
    Gets an AI response for a user message.
    Reads conversation context for AI memory, invokes agent, updates summary.
    Includes session-based message history in the prompt for continuity.
    Does NOT persist messages - they are session-based only.
    Returns dict with role and content for frontend display.
    """
    # 1. Get conversation context for AI memory
    context = await get_conversation_context(db, project_id)

    # 2. Get AI Response (passing conversation context and message history)
    ai_text = await generate_agent_response(
        db,
        project_id,
        content,
        message_history=history or [],
    )

    # 3. Update conversation summary for future interactions
    if context:
        # Append to existing summary or create new one
        current_summary = context.conversation_summary or ""
        new_summary = f"{current_summary}\nUser: {content[:100]}... | Assistant: {ai_text[:100]}..." if current_summary else f"User: {content[:100]}... | Assistant: {ai_text[:100]}..."

        await update_conversation_context(
            db,
            context,
            ConversationContextUpdate(conversation_summary=new_summary[:500]),  # Limit length
        )

    # 4. Return response for frontend (session-based, not persisted)
    return {"role": "assistant", "content": ai_text}