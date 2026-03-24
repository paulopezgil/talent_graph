from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from app.schemas import ParseEmployeeProfileAI, ParseEmployeeProfileOutput, ParseEmployeeProfilePayload
from app.services.llm_service.clients import get_llm
from app.services.llm_service.prompt_templates import PARSE_EMPLOYEE_PROMPT_TEMPLATE

parse_employee_prompt = ChatPromptTemplate.from_template(PARSE_EMPLOYEE_PROMPT_TEMPLATE)


async def parse_employee(profile: ParseEmployeeProfilePayload) -> ParseEmployeeProfileOutput:
    """Use the LLM to extract skills and experience from the employee bio and/or CV.

    Priority rules:
    - Manually provided fields (name, title, department, location, grade) always win.
    - The LLM receives both bio and cv (whichever are present) and extracts skills /
      years_experience from the combined text.
    - bio falls back to the cv text when bio is not provided, so the profile always
      carries searchable free text if any was supplied.
    """
    profile_text = []
    if profile.bio:
        profile_text.append(f"Bio:\n{profile.bio}")
    if profile.cv:
        profile_text.append(f"CV:\n{profile.cv}")

    if profile_text:
        try:
            chain = parse_employee_prompt | get_llm().with_structured_output(ParseEmployeeProfileAI)
            parsed = await chain.ainvoke({"profile_text": "\n\n".join(profile_text)})
        except Exception:
            parsed = ParseEmployeeProfileAI()
    else:
        parsed = ParseEmployeeProfileAI()

    data = parsed.model_dump()

    # Resolve bio: manual bio takes priority; fall back to cv text when bio is absent.
    profile_data = profile.model_dump()
    if not profile_data.get("bio") and profile.cv:
        profile_data["bio"] = profile.cv

    return ParseEmployeeProfileOutput(
        **profile_data,
        skills=data.get("skills", []),
        years_experience=data.get("years_experience"),
    )
