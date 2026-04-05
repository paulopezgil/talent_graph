import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.message import Message
    from backend.models.script import Script
    from backend.models.social_media import SocialMedia


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    
    # Using 1536 dimensions as per OpenAI's text-embedding-3-large default
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(1536), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="project", cascade="all, delete-orphan"
    )
    scripts: Mapped[List["Script"]] = relationship(
        "Script", back_populates="project", cascade="all, delete-orphan"
    )
    social_media: Mapped[List["SocialMedia"]] = relationship(
        "SocialMedia", back_populates="project", cascade="all, delete-orphan"
    )