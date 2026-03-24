from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import (
    ParseEmployeeProfileOutput,
    ParseEmployeeProfilePayload,
    ParsedQuery,
    QueryRequest,
    Skill,
    SkillFilter,
)


class TestSkill:
    def test_required_name(self):
        with pytest.raises(ValidationError):
            Skill()

    def test_defaults(self):
        skill = Skill(name="Python")
        assert skill.years_experience is None
        assert skill.description == ""

    def test_full_construction(self):
        skill = Skill(name="Go", years_experience=3.5, description="Systems")
        assert skill.name == "Go"
        assert skill.years_experience == 3.5


class TestParseEmployeeProfilePayload:
    def test_required_fields(self):
        with pytest.raises(ValidationError):
            ParseEmployeeProfilePayload(name="Alice", title="Dev")  # missing bio

    def test_optional_fields_default_to_none(self):
        p = ParseEmployeeProfilePayload(name="Alice", title="Dev", bio="Bio text")
        assert p.department is None
        assert p.location is None
        assert p.grade is None

    def test_full_construction(self):
        p = ParseEmployeeProfilePayload(
            name="Alice", title="Dev", bio="Bio", department="Eng", location="NYC", grade="senior"
        )
        assert p.name == "Alice"
        assert p.department == "Eng"


class TestParseEmployeeProfileOutput:
    def test_inherits_payload_and_metadata(self):
        p = ParseEmployeeProfileOutput(
            name="Bob", title="PM", bio="Product work",
            skills=[], years_experience=5,
        )
        assert p.name == "Bob"
        assert p.years_experience == 5
        assert p.skills == []

    def test_skills_default_to_empty_list(self):
        p = ParseEmployeeProfileOutput(name="Bob", title="PM", bio="Bio")
        assert p.skills == []
        assert p.years_experience is None


class TestQueryRequest:
    def test_required_query(self):
        with pytest.raises(ValidationError):
            QueryRequest()

    def test_top_k_default(self):
        req = QueryRequest(query="find a python dev")
        assert req.top_k == 5

    def test_top_k_lower_bound(self):
        with pytest.raises(ValidationError):
            QueryRequest(query="q", top_k=0)

    def test_top_k_upper_bound(self):
        with pytest.raises(ValidationError):
            QueryRequest(query="q", top_k=51)

    def test_top_k_at_boundaries(self):
        assert QueryRequest(query="q", top_k=1).top_k == 1
        assert QueryRequest(query="q", top_k=50).top_k == 50


class TestParsedQuery:
    def test_all_fields_optional(self):
        q = ParsedQuery()
        assert q.skill_filters == []
        assert q.min_years is None
        assert q.department is None
        assert q.grade is None
        assert q.location is None
        assert q.semantic_query == ""

    def test_skill_filter_construction(self):
        sf = SkillFilter(name="python", min_years=3)
        q = ParsedQuery(skill_filters=[sf])
        assert len(q.skill_filters) == 1
        assert q.skill_filters[0].name == "python"

    def test_skill_filter_min_years_optional(self):
        sf = SkillFilter(name="go")
        assert sf.min_years is None
