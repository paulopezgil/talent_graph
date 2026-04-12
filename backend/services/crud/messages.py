from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.message import Message
from backend.exceptions.classes import NotFoundError


async def get_project_messages(db: AsyncSession, project_id: UUID) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())

async def get_last_project_messages(db: AsyncSession, project_id: UUID, limit: int = 10) -> List[Message]:
    """
    Returns the last N messages for a project, ordered by creation date.
    Defaults to last 10 messages.
    """
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))

async def get_last_project_message(db: AsyncSession, project_id: UUID) -> Optional[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def get_message(db: AsyncSession, message_id: UUID) -> Optional[Message]:
    """Fetch a single message by its ID. Raises NotFoundError if not found."""
    
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if message is None:
        raise NotFoundError(f"Message with id {message_id} not found")

    return message

async def create_message(db: AsyncSession, project_id: UUID, role: str, content: str) -> Message:
    msg = Message(project_id=project_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def update_message(db: AsyncSession, msg: Message, content: str) -> Message:
    msg.content = content
    await db.commit()
    await db.refresh(msg)
    return msg

async def delete_message(db: AsyncSession, msg: Message) -> None:
    await db.delete(msg)
    await db.commit()
