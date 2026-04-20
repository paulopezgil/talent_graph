import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Text, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.conversation_context import ConversationContext
    from backend.models.script import Script
    from backend.models.social_media import SocialMedia


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, default="")
    key_topics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), default=list)
    
    # Using 1536 dimensions as per OpenAI's text-embedding-3-large default
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(1536), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    conversation_context: Mapped[Optional["ConversationContext"]] = relationship(
        "ConversationContext",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan",
    )
    script: Mapped[Optional["Script"]] = relationship(
        "Script", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    social_media: Mapped[Optional["SocialMedia"]] = relationship(
        "SocialMedia", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )