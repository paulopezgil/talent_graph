from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.schemas import ParseEmployeeProfileOutput, ParsedQuery, Skill, SkillFilter, EmployeeResult


@pytest.fixture
def client():
    mock_qdrant = MagicMock()
    mock_qdrant.get_collections.return_value = MagicMock(collections=[])
    with patch("app.services.qdrant_service.ensure_collection.qdrant", mock_qdrant):
        from main import app
        with TestClient(app) as c:
            yield c


VALID_PROFILE = {
    "name": "Alice Smith",
    "title": "Senior Python Developer",
    "bio": "10 years building Python backends.",
    "department": "Engineering",
    "location": "NYC",
    "grade": "senior",
}


class TestUploadEmployee:
    def test_returns_id_and_parsed_profile(self, client):
        parsed = ParseEmployeeProfileOutput(
            name="Alice Smith",
            title="Senior Python Developer",
            bio="10 years building Python backends.",
            skills=[Skill(name="Python", years_experience=10, description="Backend")],
            years_experience=10,
        )
        with (
            patch("app.api.v1.endpoints.parse_employee", new_callable=AsyncMock, return_value=parsed),
            patch("app.api.v1.endpoints.upsert_employee", return_value="test-uuid"),
        ):
            resp = client.post("/employees/upload", json=VALID_PROFILE)

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "test-uuid"
        assert data["parsed_profile"]["name"] == "Alice Smith"
        assert data["message"] == "Employee profile ingested successfully."

    def test_missing_required_field_returns_422(self, client):
        resp = client.post("/employees/upload", json={"name": "Alice", "title": "Dev"})
        assert resp.status_code == 422

    def test_optional_fields_are_accepted(self, client):
        parsed = ParseEmployeeProfileOutput(name="Bob", title="Dev", bio="Bio", skills=[])
        with (
            patch("app.api.v1.endpoints.parse_employee", new_callable=AsyncMock, return_value=parsed),
            patch("app.api.v1.endpoints.upsert_employee", return_value="uuid-2"),
        ):
            resp = client.post("/employees/upload", json={"name": "Bob", "title": "Dev", "bio": "Bio"})
        assert resp.status_code == 200


class TestQueryEmployees:
    def test_returns_search_results(self, client):
        mock_results = [
            EmployeeResult(
                id="uuid-1",
                name="Alice",
                title="Dev",
                bio="Bio",
                skills=[],
                score=0.9,
            )
        ]
        with (
            patch("app.api.v1.endpoints.parse_query", new_callable=AsyncMock, return_value=ParsedQuery()),
            patch("app.api.v1.endpoints.search_employees", return_value=mock_results),
        ):
            resp = client.post("/query", json={"query": "python developer"})

        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
        assert results[0]["score"] == 0.9

    def test_missing_query_returns_422(self, client):
        resp = client.post("/query", json={"top_k": 5})
        assert resp.status_code == 422

    def test_top_k_out_of_range_returns_422(self, client):
        resp = client.post("/query", json={"query": "python dev", "top_k": 0})
        assert resp.status_code == 422

    def test_empty_results(self, client):
        with (
            patch("app.api.v1.endpoints.parse_query", new_callable=AsyncMock, return_value=ParsedQuery()),
            patch("app.api.v1.endpoints.search_employees", return_value=[]),
        ):
            resp = client.post("/query", json={"query": "unicorn developer"})
        assert resp.status_code == 200
        assert resp.json() == []


class TestUploadEmployeeFile:
    def test_returns_id_and_parsed_profile(self, client):
        parsed = ParseEmployeeProfileOutput(
            name="Alice Smith",
            title="Senior Python Developer",
            bio="Extracted from PDF.",
            skills=[Skill(name="Python", years_experience=10, description="Backend")],
            years_experience=10,
        )
        with (
            patch("app.api.v1.endpoints.extract_text_from_upload", new_callable=AsyncMock, return_value="Extracted from PDF."),
            patch("app.api.v1.endpoints.parse_employee", new_callable=AsyncMock, return_value=parsed),
            patch("app.api.v1.endpoints.upsert_employee", return_value="file-uuid"),
        ):
            resp = client.post(
                "/employees/upload-file",
                data={"name": "Alice Smith", "title": "Senior Python Developer"},
                files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "file-uuid"
        assert data["parsed_profile"]["name"] == "Alice Smith"
        assert data["message"] == "Employee profile ingested successfully."

    def test_missing_name_returns_422(self, client):
        resp = client.post(
            "/employees/upload-file",
            data={"title": "Dev"},
            files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 422

    def test_missing_file_returns_422(self, client):
        resp = client.post(
            "/employees/upload-file",
            data={"name": "Alice", "title": "Dev"},
        )
        assert resp.status_code == 422

    def test_optional_fields_accepted(self, client):
        parsed = ParseEmployeeProfileOutput(name="Bob", title="Dev", bio="Bio", skills=[])
        with (
            patch("app.api.v1.endpoints.extract_text_from_upload", new_callable=AsyncMock, return_value="Bio"),
            patch("app.api.v1.endpoints.parse_employee", new_callable=AsyncMock, return_value=parsed),
            patch("app.api.v1.endpoints.upsert_employee", return_value="uuid-3"),
        ):
            resp = client.post(
                "/employees/upload-file",
                data={"name": "Bob", "title": "Dev", "department": "Eng", "location": "NYC", "grade": "senior"},
                files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
            )
        assert resp.status_code == 200


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
