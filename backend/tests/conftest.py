from __future__ import annotations

import pytest

from app.schemas import ParseEmployeeProfileOutput, ParseEmployeeProfilePayload, ParsedQuery, Skill, SkillFilter

FAKE_VECTOR = [0.1] * 1536


@pytest.fixture
def sample_payload() -> ParseEmployeeProfilePayload:
    return ParseEmployeeProfilePayload(
        name="Alice Smith",
        title="Senior Python Developer",
        bio="10 years building Python backends.",
        department="Engineering",
        location="NYC",
        grade="senior",
    )


@pytest.fixture
def sample_parsed_employee() -> ParseEmployeeProfileOutput:
    return ParseEmployeeProfileOutput(
        name="Alice Smith",
        title="Senior Python Developer",
        bio="10 years building Python backends.",
        department="Engineering",
        location="NYC",
        grade="senior",
        skills=[Skill(name="Python", years_experience=10, description="Backend")],
        years_experience=10,
    )


@pytest.fixture
def sample_parsed_query() -> ParsedQuery:
    return ParsedQuery(
        skill_filters=[SkillFilter(name="python", min_years=3)],
        grade="senior",
        semantic_query="senior python developer",
    )
