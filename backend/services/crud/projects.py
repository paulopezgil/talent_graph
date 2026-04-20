from typing import List, Optional, Sequence
from uuid import UUID
from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.project import Project
from backend.models.conversation_context import ConversationContext
from backend.schemas.project import ProjectUpdate
from backend.exceptions import NotFoundError


async def get_projects(db: AsyncSession) -> Sequence[Row]:
    result = await db.execute(
        select(Project.id, Project.title, Project.updated_at)
        .order_by(Project.updated_at.desc())
    )
    return result.all()

async def get_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if project is None:
        raise NotFoundError(f"Project with id {project_id} not found")

    return project

async def create_project(db: AsyncSession) -> Project:
    # Initialize an empty project
    project = Project(title="", description="")
    db.add(project)
    await db.flush()  # Get the project ID without committing

    # Create associated conversation context
    conversation_context = ConversationContext(project_id=project.id)
    db.add(conversation_context)

    await db.commit()
    await db.refresh(project)
    return project

async def update_project(db: AsyncSession, project: Project, project_in: ProjectUpdate) -> Project:
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project
