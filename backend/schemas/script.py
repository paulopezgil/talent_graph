from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ScriptBase(BaseModel):
    content: str


class ScriptCreate(ScriptBase):
    project_id: UUID


class ScriptUpdate(BaseModel):
    content: Optional[str] = None


class ScriptResponse(ScriptBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
