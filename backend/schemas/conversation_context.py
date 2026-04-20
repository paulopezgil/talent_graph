from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class ConversationContextResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_intent: Optional[str] = ""
    user_preferences: Optional[Dict[str, Any]] = {}
    conversation_summary: Optional[str] = ""
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConversationContextUpdate(BaseModel):
    user_intent: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    conversation_summary: Optional[str] = None