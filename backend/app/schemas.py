from __future__ import annotations

from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str = Field(..., description="Name of the skill or technology")
    years_experience: float | None = Field(None, description="Years of experience with this specific skill")
    description: str = Field("", description="Brief description of proficiency or context")


class ParseEmployeeProfilePayload(BaseModel):
    name: str | None = Field(None, description="Full name of the employee")
    title: str | None = Field(None, description="Current job title or role")
    bio: str | None = Field(None, description="Free-text employee profile / resume")
    cv: str | None = Field(None, description="Raw CV / curriculum vitae text")
    department: str | None = Field(None, description="Department or business unit")
    location: str | None = Field(None, description="Geographic location (city, country)")
    grade: str | None = Field(None, description="Seniority grade (e.g. junior, mid, senior, lead)")


class ParseEmployeeProfileAI(BaseModel):
    """Structured fields expected from LLM extraction of an employee bio."""
    skills: list[Skill] = Field(default_factory=list, description="List of extracted skills with experience details")
    years_experience: float | None = Field(None, description="Total years of professional experience")


class ParseEmployeeProfileOutput(ParseEmployeeProfilePayload, ParseEmployeeProfileAI):
    """Parsed employee profile with structured metadata extracted from free text."""

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural-language talent search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Maximum number of results to return")


class EmployeeResult(ParseEmployeeProfileOutput):
    id: str = Field(..., description="Unique identifier of the employee record")
    score: float = Field(..., description="Relevance score from vector search")


class SkillFilter(BaseModel):
    name: str = Field(..., description="Skill name to match")
    min_years: float | None = Field(None, description="Minimum years of experience for this skill")


class ParsedQuery(BaseModel):
    skill_filters: list[SkillFilter] = Field(default_factory=list, description="Per-skill filters with optional min experience")
    min_years: float | None = Field(None, description="Minimum total years of experience")
    department: str | None = Field(None, description="Department filter")
    grade: str | None = Field(None, description="Grade filter")
    location: str | None = Field(None, description="Location filter")
    semantic_query: str = Field("", description="Rephrased query for embedding search")

