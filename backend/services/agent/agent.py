from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError
import logging

from backend.core.config import settings
from backend.services.agent.prompts import SYSTEM_PROMPT_STATIC, build_dynamic_context
from backend.services.agent.tools import project
from backend.services.agent.tools import script
from backend.services.agent.tools import social_media
from backend.services.agent.utils import build_message_history
from backend.exceptions import AgentError

logger = logging.getLogger(__name__)

@dataclass
class ProjectAgentDeps:
    db: AsyncSession
    project_id: UUID


# Initialize the Pydantic AI agent
vidplan_agent = Agent(
    settings.ai_model,
    deps_type=ProjectAgentDeps,
    retries=2,
    system_prompt=SYSTEM_PROMPT_STATIC,
    defer_model_check=True  # Don't validate API key until first run
)


@vidplan_agent.system_prompt
async def add_dynamic_context(ctx: RunContext[ProjectAgentDeps]) -> str:
    """Injects the current database state of the project into the system prompt."""
    return await build_dynamic_context(ctx.deps.db, ctx.deps.project_id)


@vidplan_agent.tool
async def update_project_tab(ctx: RunContext[ProjectAgentDeps], title: str, description: str) -> str:
    """Updates the project title and description in the database (Project Tab)."""
    return await project.update_tab(ctx.deps.db, ctx.deps.project_id, title, description)


@vidplan_agent.tool
async def update_script_tab(ctx: RunContext[ProjectAgentDeps], content: str) -> str:
    """Updates or creates the script content in the database (Script Tab)."""
    return await script.update_tab(ctx.deps.db, ctx.deps.project_id, content)


@vidplan_agent.tool
async def update_social_media_tab(
    ctx: RunContext[ProjectAgentDeps], 
    youtube_title: Optional[str] = None,
    youtube_description: Optional[str] = None,
    instagram_description: Optional[str] = None,
    tiktok_description: Optional[str] = None,
    twitter_post: Optional[str] = None,
    linkedin_post: Optional[str] = None
) -> str:
    """Updates or creates the social media content in the database (Social Network Tab)."""
    return await social_media.update_tab(
        ctx.deps.db, 
        ctx.deps.project_id,
        youtube_title,
        youtube_description,
        instagram_description,
        tiktok_description,
        twitter_post,
        linkedin_post
    )


async def generate_agent_response(db: AsyncSession, project_id: UUID, user_prompt: str, message_history: list) -> str:
    """
    Orchestrates the AI invocation.
    Receives message history as parameter, formats it, and runs the agent.
    """

    # Convert to Pydantic AI ModelMessage format and initialize dependencies
    history = build_message_history(message_history)
    deps = ProjectAgentDeps(db=db, project_id=project_id)

    # Run the agent with the user prompt, dependencies, and message history
    try:
        result = await vidplan_agent.run(user_prompt, deps=deps, message_history=history)
        return result.output
    except AgentRunError as err:
        logger.exception(f"Agent error for project {project_id}")
        raise AgentError(message=str(err), original_error=err)