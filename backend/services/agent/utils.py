from typing import List, Dict
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart
import logging

logger = logging.getLogger(__name__)


def build_message_history(history: List[Dict[str, str]]) -> list[ModelMessage]:
    """Convert session-based message history (list of dicts) to Pydantic AI format."""
    messages = []
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if not content:
            continue

        if role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif role == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
        else:
            logger.warning(f"Skipping message with unknown role: {role}")

    return messages