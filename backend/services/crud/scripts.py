from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.script import Script
from backend.schemas import ScriptCreate, ScriptUpdate

async def get_project_scripts(db: AsyncSession, project_id: UUID) -> List[Script]:
    result = await db.execute(
        select(Script).where(Script.project_id == project_id).order_by(Script.created_at.desc())
    )
    return list(result.scalars().all())

async def get_script(db: AsyncSession, script_id: UUID) -> Optional[Script]:
    result = await db.execute(select(Script).where(Script.id == script_id))
    return result.scalar_one_or_none()

async def create_script(db: AsyncSession, script_in: ScriptCreate) -> Script:
    script = Script(**script_in.model_dump())
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
