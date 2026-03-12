from __future__ import annotations

from unittest.mock import MagicMock, patch

from qdrant_client.models import NestedCondition

from app.schemas import ParsedQuery, SkillFilter
from app.services.qdrant_service.search_employees import search_employees

FAKE_VECTOR = [0.1] * 1536


def _make_hit(id="abc-123", score=0.95, payload=None):
    hit = MagicMock()
    hit.id = id
    hit.score = score
    hit.payload = payload or {
        "name": "Alice",
        "title": "Developer",
        "bio": "Experienced dev",
        "skills": [{"name": "python", "years_experience": 5, "description": "Backend"}],
        "years_experience": 5,
        "department": "Engineering",
        "grade": "senior",
        "location": "NYC",
    }
    return hit


@patch("app.services.qdrant_service.search_employees.embeddings")
@patch("app.services.qdrant_service.search_employees.qdrant")
def test_builds_nested_skill_filter(mock_qdrant, mock_embeddings):
    mock_embeddings.embed_query.return_value = FAKE_VECTOR
    mock_qdrant.search.return_value = [_make_hit()]

    parsed = ParsedQuery(
        skill_filters=[SkillFilter(name="python", min_years=3)],
        semantic_query="python developer",
    )
    results = search_employees(parsed, "python developer", top_k=5)

    call_kwargs = mock_qdrant.search.call_args.kwargs
    query_filter = call_kwargs["query_filter"]
    assert query_filter is not None
    assert len(query_filter.must) == 1
    assert isinstance(query_filter.must[0], NestedCondition)
    assert query_filter.must[0].nested.key == "skills"

    assert len(results) == 1
    assert results[0].name == "Alice"
    assert results[0].score == 0.95


@patch("app.services.qdrant_service.search_employees.embeddings")
@patch("app.services.qdrant_service.search_employees.qdrant")
def test_builds_department_and_grade_filters(mock_qdrant, mock_embeddings):
    mock_embeddings.embed_query.return_value = FAKE_VECTOR
    mock_qdrant.search.return_value = []

    parsed = ParsedQuery(
        department="Engineering",
        grade="senior",
        semantic_query="engineer",
    )
    search_employees(parsed, "engineer", top_k=5)

    call_kwargs = mock_qdrant.search.call_args.kwargs
    query_filter = call_kwargs["query_filter"]
    assert query_filter is not None
    assert len(query_filter.must) == 2
    field_keys = {c.key for c in query_filter.must}
    assert "department" in field_keys
    assert "grade" in field_keys


@patch("app.services.qdrant_service.search_employees.embeddings")
@patch("app.services.qdrant_service.search_employees.qdrant")
def test_no_filter_when_empty_query(mock_qdrant, mock_embeddings):
    mock_embeddings.embed_query.return_value = FAKE_VECTOR
    mock_qdrant.search.return_value = []

    parsed = ParsedQuery(semantic_query="anything")
    search_employees(parsed, "anything", top_k=10)

    call_kwargs = mock_qdrant.search.call_args.kwargs
    assert call_kwargs["query_filter"] is None
    assert call_kwargs["limit"] == 10


@patch("app.services.qdrant_service.search_employees.embeddings")
@patch("app.services.qdrant_service.search_employees.qdrant")
def test_maps_multiple_results(mock_qdrant, mock_embeddings):
    mock_embeddings.embed_query.return_value = FAKE_VECTOR
    mock_qdrant.search.return_value = [
        _make_hit(
            id="id-1",
            score=0.9,
            payload={
                "name": "Bob",
                "title": "Designer",
                "bio": "UI/UX expert",
                "skills": [],
                "years_experience": 3,
                "department": "Design",
                "grade": "mid",
                "location": "London",
            },
        ),
        _make_hit(
            id="id-2",
            score=0.7,
            payload={
                "name": "Carol",
                "title": "PM",
                "bio": "Product management",
                "skills": [],
                "years_experience": 8,
                "department": None,
                "grade": None,
                "location": None,
            },
        ),
    ]

    parsed = ParsedQuery(semantic_query="designer")
    results = search_employees(parsed, "designer", top_k=5)

    assert len(results) == 2
    assert results[0].id == "id-1"
    assert results[0].name == "Bob"
    assert results[0].score == 0.9
    assert results[1].id == "id-2"
    assert results[1].name == "Carol"
    assert results[1].score == 0.7
