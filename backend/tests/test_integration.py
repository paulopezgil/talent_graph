from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.schemas import (
    EmployeeResult,
    ParsedEmployeeProfile,
    ParsedQuery,
    Skill,
    SkillFilter,
)


@pytest.fixture
def client():
    """FastAPI test client with Qdrant mocked out during startup."""
    mock_qdrant = MagicMock()
    mock_qdrant.get_collections.return_value = MagicMock(collections=[])

    with patch("app.services.qdrant_service.ensure_collection.qdrant", mock_qdrant):
        from main import app

        with TestClient(app) as c:
            yield c


def test_upload_and_search_round_trip(client):
    """Full upload → search flow through the API with mocked services."""
    # ── Upload ──────────────────────────────────────────────────────────────
    parsed_profile = ParsedEmployeeProfile(
        name="Alice Smith",
        title="Senior Python Developer",
        bio="10 years building Python backends.",
        skills=[Skill(name="Python", years_experience=10, description="Backend")],
        years_experience=10,
        department="Engineering",
        location="NYC",
        grade="senior",
    )

    with (
        patch(
            "app.api.v1.endpoints.parse_employee_profile",
            new_callable=AsyncMock,
            return_value=parsed_profile,
        ),
        patch(
            "app.api.v1.endpoints.upsert_employee",
            return_value="test-uuid-123",
        ),
    ):
        upload_resp = client.post(
            "/employees/upload",
            json={
                "name": "Alice Smith",
                "title": "Senior Python Developer",
                "bio": "10 years building Python backends.",
                "department": "Engineering",
                "location": "NYC",
                "grade": "senior",
            },
        )

    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["id"] == "test-uuid-123"
    assert upload_data["parsed_profile"]["name"] == "Alice Smith"
    assert len(upload_data["parsed_profile"]["skills"]) == 1

    # ── Search ──────────────────────────────────────────────────────────────
    mock_parsed_query = ParsedQuery(
        skill_filters=[SkillFilter(name="python", min_years=5)],
        semantic_query="senior python developer",
    )
    mock_results = [
        EmployeeResult(
            id="test-uuid-123",
            name="Alice Smith",
            title="Senior Python Developer",
            bio="10 years building Python backends.",
            skills=[Skill(name="Python", years_experience=10, description="Backend")],
            years_experience=10,
            department="Engineering",
            location="NYC",
            grade="senior",
            score=0.95,
        )
    ]

    with (
        patch(
            "app.api.v1.endpoints.parse_query",
            new_callable=AsyncMock,
            return_value=mock_parsed_query,
        ),
        patch(
            "app.api.v1.endpoints.search_employees",
            return_value=mock_results,
        ),
    ):
        search_resp = client.post(
            "/query",
            json={"query": "Senior Python dev with 5+ years", "top_k": 5},
        )

    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) == 1
    assert results[0]["name"] == "Alice Smith"
    assert results[0]["score"] == 0.95
    assert results[0]["skills"][0]["name"] == "Python"


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
