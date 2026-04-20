from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatInput(BaseModel):
    content: str
    history: Optional[List[ChatMessage]] = []  # Session-based message history


class ChatResponse(BaseModel):
    role: str
    content: str
    model_config = ConfigDict(from_attributes=True)