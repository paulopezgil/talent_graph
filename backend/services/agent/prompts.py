from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.services.crud.projects import get_project
from backend.services.crud.scripts import get_project_script
from backend.services.crud.social_media import get_project_social_media
from backend.services.crud.conversation_context import get_conversation_context

SYSTEM_PROMPT_STATIC = """
You are VidPlan AI, a helpful content creator assistant.
You help brainstorm, plan, and generate video scripts and social media posts.
You have the ability to read the current project context and update the project, script, and social media tabs.
When asked to generate or update content, use the provided tools to save your work to the database.
Always be concise, creative, and professional.
""".strip()

async def build_dynamic_context(db: AsyncSession, project_id: UUID) -> str:
    project = await get_project(db, project_id)
    script = await get_project_script(db, project_id)
    social_media = await get_project_social_media(db, project_id)
    conversation_context = await get_conversation_context(db, project_id)
    
    context = ["Here is the current state of the user's workspace:"]
    
    # Project context
    if project:
        project_info = f"Title: {project.title}\nDescription: {project.description}"
        if project.summary:
            project_info += f"\nSummary: {project.summary}"
        if project.key_topics:
            project_info += f"\nKey Topics: {', '.join(project.key_topics)}"
        context.append(f"\n--- Project Tab ---\n{project_info}")
    else:
        context.append("\n--- Project Tab ---\nNo project found.")
        
    # Conversation context (AI memory)
    if conversation_context:
        ctx_parts = []
        if conversation_context.user_intent:
            ctx_parts.append(f"User Intent: {conversation_context.user_intent}")
        if conversation_context.user_preferences:
            prefs = conversation_context.user_preferences
            prefs_str = ", ".join([f"{k}: {v}" for k, v in prefs.items()])
            ctx_parts.append(f"User Preferences: {prefs_str}")
        if conversation_context.conversation_summary:
            ctx_parts.append(f"Conversation Summary: {conversation_context.conversation_summary}")
        
        if ctx_parts:
            context.append(f"\n--- Conversation Context ---\n" + "\n".join(ctx_parts))
    
    # Script context
    if script:
        context.append(f"\n--- Script Tab ---\nContent: {script.content}")
    else:
        context.append("\n--- Script Tab ---\nNo script generated yet.")
        
    # Social media context
    if social_media:
        context.append(f"\n--- Social Network Tab ---\nYouTube Title: {social_media.youtube_title}\nYouTube Description: {social_media.youtube_description}\nTwitter Post: {social_media.twitter_post}\nLinkedIn Post: {social_media.linkedin_post}")
    else:
        context.append("\n--- Social Network Tab ---\nNo social media content generated yet.")
        
    context.append("\nUse your tools to update these tabs when requested or when you generate new content.")
    return "\n".join(context)
