import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.project import Project


class SocialMedia(Base):
    __tablename__ = "social_media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True)
    
    youtube_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    youtube_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instagram_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tiktok_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    twitter_post: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linkedin_post: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="social_media")
