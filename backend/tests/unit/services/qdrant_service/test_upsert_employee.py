from __future__ import annotations

from unittest.mock import MagicMock, call, patch

from app.schemas import ParseEmployeeProfileOutput, Skill
from app.services.qdrant_service.upsert_employee import upsert_employee

FAKE_VECTOR = [0.1] * 1536


def _make_parsed(**kwargs) -> ParseEmployeeProfileOutput:
    defaults = dict(
        name="Alice",
        title="Senior Dev",
        bio="10 years in Python",
        department="Engineering",
        location="NYC",
        grade="senior",
        skills=[Skill(name="Python", years_experience=10, description="Backend")],
        years_experience=10,
    )
    return ParseEmployeeProfileOutput(**{**defaults, **kwargs})


@patch("app.services.qdrant_service.upsert_employee.qdrant")
@patch("app.services.qdrant_service.upsert_employee.get_embeddings")
def test_returns_uuid_string(mock_get_embeddings, mock_qdrant):
    mock_get_embeddings.return_value.embed_query.return_value = FAKE_VECTOR
    result = upsert_employee(_make_parsed())
    assert isinstance(result, str)
    assert len(result) == 36  # UUID format


@patch("app.services.qdrant_service.upsert_employee.qdrant")
@patch("app.services.qdrant_service.upsert_employee.get_embeddings")
def test_embeds_name_title_bio(mock_get_embeddings, mock_qdrant):
    mock_get_embeddings.return_value.embed_query.return_value = FAKE_VECTOR
    parsed = _make_parsed(name="Bob", title="PM", bio="Product work")
    upsert_employee(parsed)
    mock_get_embeddings.return_value.embed_query.assert_called_once_with("Bob PM Product work")


@patch("app.services.qdrant_service.upsert_employee.qdrant")
@patch("app.services.qdrant_service.upsert_employee.get_embeddings")
def test_payload_fields_stored_correctly(mock_get_embeddings, mock_qdrant):
    mock_get_embeddings.return_value.embed_query.return_value = FAKE_VECTOR
    parsed = _make_parsed()
    upsert_employee(parsed)

    point = mock_qdrant.upsert.call_args.kwargs["points"][0]
    payload = point.payload
    assert payload["name"] == "Alice"
    assert payload["title"] == "Senior Dev"
    assert payload["bio"] == "10 years in Python"
    assert payload["department"] == "Engineering"
    assert payload["location"] == "NYC"
    assert payload["grade"] == "senior"
    assert payload["years_experience"] == 10


@patch("app.services.qdrant_service.upsert_employee.qdrant")
@patch("app.services.qdrant_service.upsert_employee.get_embeddings")
def test_skill_names_are_lowercased(mock_get_embeddings, mock_qdrant):
    mock_get_embeddings.return_value.embed_query.return_value = FAKE_VECTOR
    parsed = _make_parsed(skills=[
        Skill(name="Python", years_experience=5, description=""),
        Skill(name="FastAPI", years_experience=2, description=""),
    ])
    upsert_employee(parsed)

    point = mock_qdrant.upsert.call_args.kwargs["points"][0]
    assert point.payload["skill_names"] == ["python", "fastapi"]


@patch("app.services.qdrant_service.upsert_employee.qdrant")
@patch("app.services.qdrant_service.upsert_employee.get_embeddings")
def test_each_call_returns_unique_id(mock_get_embeddings, mock_qdrant):
    mock_get_embeddings.return_value.embed_query.return_value = FAKE_VECTOR
    parsed = _make_parsed()
    id1 = upsert_employee(parsed)
    id2 = upsert_employee(parsed)
    assert id1 != id2
