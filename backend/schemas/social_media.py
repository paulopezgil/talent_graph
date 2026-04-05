from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class SocialMediaBase(BaseModel):
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    instagram_description: Optional[str] = None
    tiktok_description: Optional[str] = None
    twitter_post: Optional[str] = None
    linkedin_post: Optional[str] = None


class SocialMediaCreate(SocialMediaBase):
    project_id: UUID


class SocialMediaUpdate(BaseModel):
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    instagram_description: Optional[str] = None
    tiktok_description: Optional[str] = None
    twitter_post: Optional[str] = None
    linkedin_post: Optional[str] = None


class SocialMediaResponse(SocialMediaBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
