from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas import ParseEmployeeProfileAI, ParseEmployeeProfilePayload
from app.services.llm_service.parse_employee import parse_employee


def _mock_chain(result: ParseEmployeeProfileAI) -> AsyncMock:
    """Return a mock LangChain chain whose ainvoke returns structured output."""
    chain = AsyncMock()
    chain.ainvoke = AsyncMock(return_value=result)
    return chain


@pytest.mark.asyncio
async def test_extracts_skills_and_experience():
    parsed = ParseEmployeeProfileAI(
        skills=[
            {"name": "Python", "years_experience": 5, "description": "Backend"},
            {"name": "FastAPI", "years_experience": 2, "description": "REST APIs"},
        ],
        years_experience=7,
    )
    mock = _mock_chain(parsed)

    with patch(
        "app.services.llm_service.parse_employee.parse_employee_prompt"
    ) as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)

        profile = ParseEmployeeProfilePayload(
            name="Alice", title="Senior Dev", bio="Experienced developer"
        )
        result = await parse_employee(profile)

    assert result.name == "Alice"
    assert result.title == "Senior Dev"
    assert result.bio == "Experienced developer"
    assert len(result.skills) == 2
    assert result.skills[0].name == "Python"
    assert result.skills[0].years_experience == 5
    assert result.skills[1].name == "FastAPI"
    assert result.years_experience == 7


@pytest.mark.asyncio
async def test_handles_malformed_llm_response():
    mock = AsyncMock()
    mock.ainvoke = AsyncMock(side_effect=ValueError("bad response"))

    with patch(
        "app.services.llm_service.parse_employee.parse_employee_prompt"
    ) as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)

        profile = ParseEmployeeProfilePayload(name="Bob", title="Dev", bio="Some bio")
        result = await parse_employee(profile)

    assert result.name == "Bob"
    assert result.skills == []
    assert result.years_experience is None


@pytest.mark.asyncio
async def test_preserves_optional_fields():
    parsed = ParseEmployeeProfileAI(skills=[], years_experience=3)
    mock = _mock_chain(parsed)

    with patch(
        "app.services.llm_service.parse_employee.parse_employee_prompt"
    ) as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)

        profile = ParseEmployeeProfilePayload(
            name="Carol",
            title="Manager",
            bio="Bio",
            department="Engineering",
            location="NYC",
            grade="senior",
        )
        result = await parse_employee(profile)

    assert result.department == "Engineering"
    assert result.location == "NYC"
    assert result.grade == "senior"
    assert result.years_experience == 3
