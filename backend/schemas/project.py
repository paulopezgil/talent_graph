from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ProjectListResponse(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str
    summary: Optional[str] = ""
    key_topics: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    key_topics: Optional[List[str]] = None
