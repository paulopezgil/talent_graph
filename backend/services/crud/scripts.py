from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.script import Script
from backend.schemas.script import ScriptUpdate
from backend.exceptions.classes import NotFoundError


async def get_project_script(db: AsyncSession, project_id: UUID) -> Optional[Script]:
    result = await db.execute(select(Script).where(Script.project_id == project_id))
    script = result.scalar_one_or_none()

    if script is None:
        raise NotFoundError(f"Script for project with id {project_id} not found")

    return script


async def create_script(db: AsyncSession, project_id: UUID, content: str) -> Script:
    script = Script(project_id=project_id, content=content)
    db.add(script)
    await db.commit()
    await db.refresh(script)
    return script

async def update_script(db: AsyncSession, script: Script, script_in: ScriptUpdate) -> Script:
    update_data = script_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(script, field, value)
    await db.commit()
    await db.refresh(script)
    return script
