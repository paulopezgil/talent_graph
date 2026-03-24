from __future__ import annotations
from typing import Any
from fastapi import APIRouter, File, Form, UploadFile
from app.schemas import EmployeeResult, ParseEmployeeProfileOutput, ParseEmployeeProfilePayload, QueryRequest
from app.services.llm_service import parse_employee, parse_query
from app.services.qdrant_service import upsert_employee, search_employees
from app.services.file_service import extract_text_from_upload

router = APIRouter()


@router.post("/employees/upload", response_model=dict[str, Any])
async def upload_employee(profile: ParseEmployeeProfilePayload):
    """Ingest an employee profile: extract metadata via LLM, embed, and store."""
    parsed = await parse_employee(profile)
    point_id = upsert_employee(parsed)

    return {
        "id": point_id,
        "parsed_profile": parsed.model_dump(),
        "message": "Employee profile ingested successfully.",
    }


@router.post("/employees/upload-file", response_model=dict[str, Any])
async def upload_employee_file(
    file: UploadFile = File(...),
    name: str | None = Form(None),
    title: str | None = Form(None),
    department: str | None = Form(None),
    location: str | None = Form(None),
    grade: str | None = Form(None),
):
    """Ingest an employee profile from a file (PDF, DOCX, or image): extract text, extract metadata via LLM, embed, and store."""
    bio = await extract_text_from_upload(file)
    profile = ParseEmployeeProfilePayload(name=name, title=title, bio=bio, department=department, location=location, grade=grade)
    parsed = await parse_employee(profile)
    point_id = upsert_employee(parsed)

    return {
        "id": point_id,
        "parsed_profile": parsed.model_dump(),
        "message": "Employee profile ingested successfully.",
    }


@router.post("/query", response_model=list[EmployeeResult])
async def query_employees(req: QueryRequest):
    """Metadata-filtered vector search over employee profiles."""
    parsed = await parse_query(req.query)
    results = search_employees(parsed, req.query, req.top_k)
    return results


@router.get("/health")
async def health():
    return {"status": "ok"}
