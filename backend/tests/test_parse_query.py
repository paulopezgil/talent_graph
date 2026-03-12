from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm_service.parse_query import parse_query


def _mock_chain(data: dict) -> AsyncMock:
    """Return a mock LangChain chain whose ainvoke returns JSON content."""
    result = MagicMock()
    result.content = json.dumps(data)
    chain = AsyncMock()
    chain.ainvoke = AsyncMock(return_value=result)
    return chain


@pytest.mark.asyncio
async def test_parses_skill_filters():
    llm_data = {
        "skill_filters": [{"name": "python", "min_years": 3}],
        "min_years": 5,
        "department": None,
        "grade": "senior",
        "location": None,
        "semantic_query": "senior python developer",
    }
    mock = _mock_chain(llm_data)

    with patch("app.services.llm_service.parse_query.QUERY_PROMPT") as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)
        result = await parse_query("Senior Python dev with 5+ years")

    assert len(result.skill_filters) == 1
    assert result.skill_filters[0].name == "python"
    assert result.skill_filters[0].min_years == 3
    assert result.min_years == 5
    assert result.grade == "senior"
    assert result.semantic_query == "senior python developer"


@pytest.mark.asyncio
async def test_falls_back_on_malformed_response():
    bad_result = MagicMock()
    bad_result.content = "not json"
    mock = AsyncMock()
    mock.ainvoke = AsyncMock(return_value=bad_result)

    with patch("app.services.llm_service.parse_query.QUERY_PROMPT") as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)
        result = await parse_query("find me a designer")

    assert result.skill_filters == []
    assert result.semantic_query == "find me a designer"


@pytest.mark.asyncio
async def test_parses_multiple_filters():
    llm_data = {
        "skill_filters": [
            {"name": "react", "min_years": 2},
            {"name": "typescript", "min_years": None},
        ],
        "min_years": None,
        "department": "Frontend",
        "grade": None,
        "location": "London",
        "semantic_query": "frontend developer with React and TypeScript",
    }
    mock = _mock_chain(llm_data)

    with patch("app.services.llm_service.parse_query.QUERY_PROMPT") as mock_prompt:
        mock_prompt.__or__ = MagicMock(return_value=mock)
        result = await parse_query("Frontend React/TS dev in London")

    assert len(result.skill_filters) == 2
    assert result.skill_filters[0].name == "react"
    assert result.skill_filters[1].name == "typescript"
    assert result.department == "Frontend"
    assert result.location == "London"
