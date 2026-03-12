from __future__ import annotations
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"

    # Qdrant
    qdrant_host: str = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    collection_name: str = "employees"
    embed_dim: int = 1536  # text-embedding-ada-002

    class Config:
        env_file = ".env"


settings = Settings()
