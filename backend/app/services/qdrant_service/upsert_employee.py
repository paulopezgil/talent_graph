from __future__ import annotations

import uuid

from qdrant_client.models import PointStruct

from app.core.config import settings
from app.schemas import ParseEmployeeProfileOutput
from app.services.llm_service.clients import get_embeddings
from app.services.qdrant_service.client import qdrant


def upsert_employee(parsed: ParseEmployeeProfileOutput) -> str:
    """Embed and store a parsed employee profile in Qdrant."""
    text_for_embedding = f"{parsed.name} {parsed.title} {parsed.bio}"
    vector = get_embeddings().embed_query(text_for_embedding)

    point_id = str(uuid.uuid4())
    qdrant.upsert(
        collection_name=settings.collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "name": parsed.name,
                    "title": parsed.title,
                    "bio": parsed.bio,
                    "skills": [s.model_dump() for s in parsed.skills],
                    "skill_names": [s.name.lower() for s in parsed.skills],
                    "years_experience": parsed.years_experience,
                    "department": parsed.department,
                    "grade": parsed.grade,
                    "location": parsed.location,
                },
            )
        ],
    )
    return point_id
