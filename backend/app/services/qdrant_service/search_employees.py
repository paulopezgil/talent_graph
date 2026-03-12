from __future__ import annotations

from typing import Any

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
    Nested,
    NestedCondition,
    Range,
)

from app.core.config import settings
from app.schemas import EmployeeResult, ParsedQuery
from app.services.llm_service.clients import embeddings
from app.services.qdrant_service.client import qdrant


def search_employees(
    parsed: ParsedQuery,
    raw_query: str,
    top_k: int,
) -> list[EmployeeResult]:
    """Run a metadata-filtered vector search and return ranked results."""
    conditions: list[Any] = []
    for sf in parsed.skill_filters:
        nested_conditions = [
            FieldCondition(key="name", match=MatchValue(value=sf.name.lower()))
        ]
        if sf.min_years is not None:
            nested_conditions.append(
                FieldCondition(key="years_experience", range=Range(gte=sf.min_years))
            )
        conditions.append(
            NestedCondition(
                nested=Nested(
                    key="skills",
                    filter=Filter(must=nested_conditions),
                )
            )
        )
    if parsed.min_years is not None:
        conditions.append(
            FieldCondition(
                key="years_experience", range=Range(gte=parsed.min_years)
            )
        )
    if parsed.department:
        conditions.append(
            FieldCondition(key="department", match=MatchValue(value=parsed.department))
        )
    if parsed.grade:
        conditions.append(
            FieldCondition(key="grade", match=MatchValue(value=parsed.grade))
        )
    if parsed.location:
        conditions.append(
            FieldCondition(key="location", match=MatchValue(value=parsed.location))
        )

    search_filter = Filter(must=conditions) if conditions else None
    query_vector = embeddings.embed_query(parsed.semantic_query or raw_query)

    hits = qdrant.search(
        collection_name=settings.collection_name,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=top_k,
    )

    results: list[EmployeeResult] = []
    for hit in hits:
        p = hit.payload or {}
        results.append(
            EmployeeResult(
                id=str(hit.id),
                name=p.get("name", ""),
                title=p.get("title", ""),
                bio=p.get("bio", ""),
                skills=p.get("skills", []),
                years_experience=p.get("years_experience"),
                department=p.get("department"),
                grade=p.get("grade"),
                location=p.get("location"),
                score=hit.score,
            )
        )
    return results
