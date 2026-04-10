from typing import List
from backend.models.message import Message
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart
import logging

logger = logging.getLogger(__name__)

def build_message_history(db_messages: List[Message]) -> list[ModelMessage]:
    """Convert DB messages to Pydantic AI ModelMessage history."""
    history = []
    for msg in db_messages:
        if not msg.content:
            logger.warning(f"Skipping message ID {msg.id} due to missing content")
            continue
        if not msg.role:
            logger.warning(f"Skipping message ID {msg.id} due to missing role")
            continue
        if msg.role == "user":
            history.append(ModelRequest(parts=[TextPart(content=msg.content)]))
        elif msg.role == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=msg.content)]))
    return history
