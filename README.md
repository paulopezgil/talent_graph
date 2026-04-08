# VidPlan AI: Intelligent Content Creation Assistant

**VidPlan AI** (formerly Talent Stream AI) is an AI-powered content creation platform that streamlines video production workflows. It combines conversational AI with structured content generation to help creators transform ideas into polished scripts, social media captions, and organized project plans.

## 🎯 The Problem

Content creators face significant challenges in video production:
- **Ideation to execution gaps** - Great ideas often get lost in translation between brainstorming and final content
- **Workflow fragmentation** - Switching between chat interfaces, script editors, and social media tools
- **Context loss** - Previous discussions and decisions aren't preserved for future reference
- **Manual repetition** - Recreating similar content across different platforms

## 💡 The Solution

VidPlan AI provides a unified workspace where creators can:
1. **Brainstorm naturally** with an AI assistant in conversational mode
2. **Execute seamlessly** as the AI transforms discussions into structured content
3. **Organize efficiently** with a tab-based interface that maps directly to production workflows

The system intelligently separates **idea generation** from **content creation**, ensuring that creative exploration doesn't interfere with final output quality.

## 🚀 Core Features

### 🤖 Dual-Mode AI Agent
- **Brainstorming Mode**: Free-form conversation for exploring ideas, refining concepts, and strategic planning
- **Execution Mode**: Structured content generation that directly updates scripts, captions, and project documentation

### 🗂️ Unified Workspace
- **Project-centric organization**: All content related to a video project in one place
- **Tab-based interface**: 
  - **Project Tab**: Metadata, objectives, and production notes
  - **Chat Tab**: Conversational interface with the AI assistant
  - **Script Tab**: Generated video scripts with scene-by-scene breakdowns
  - **Social Network Tab**: Platform-optimized captions and descriptions

### 🔄 Intelligent Workflow
1. **Create Project**: Start with a title and basic concept
2. **Brainstorm**: Discuss ideas with the AI in natural language
3. **Execute**: Command the AI to generate specific content types
4. **Refine**: Manually edit AI-generated content as needed
5. **Export**: Use generated content across platforms

## 🐳 Quick Start (Docker)

Get VidPlan AI running in minutes with Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd vidplan_ai

# Set up environment (copy example and add your API key)
cp .env.example .env
# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here

# Start all services
docker compose up --build

# Access the application:
# - Frontend: http://localhost:8501
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Database: localhost:5432 (user: admin, password: password)
```

**Services Started:**
- ✅ **PostgreSQL with PGVector** - Vector-enabled database for semantic search
- ✅ **FastAPI Backend** - REST API with AI agent orchestration
- ✅ **Streamlit Frontend** - Interactive web interface

**Environment Variables:**
The application uses the following key environment variables (configured in `.env`):
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `AI_MODEL`: LLM provider and model (default: `openai:gpt-4o-mini`)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials
- `API_URL`: Backend API URL for frontend (default: `http://backend:8000`)

## 🛠️ Tech Stack

### Backend & AI
- **Framework**: FastAPI (async Python)
- **AI Orchestration**: Pydantic AI with structured outputs
- **Database**: PostgreSQL + PGVector for hybrid structured/vector storage
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Streamlit for rapid UI development
- **Layout**: Custom multi-tab workspace with project sidebar

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Multi-LLM Support**: OpenAI, Anthropic, Google Gemini, DeepSeek, Mistral, Groq, Cohere

### Development
- **Testing**: pytest with async fixtures
- **Code Quality**: ruff, black, mypy
- **Environment Management**: python-dotenv, pydantic-settings

## 📚 Technical Documentation

Detailed architecture and implementation documentation is available in the `/docs` directory:

- **[Backend Architecture](docs/backend_architecture.md)** - Detailed breakdown of services, database schema, and AI agent implementation
- **[Frontend Architecture](docs/frontend_architecture.md)** - UI structure, component organization, and workflow patterns

## 🎯 Use Cases

### For Content Creators
- YouTube video script generation
- Social media content planning
- Video project organization
- Cross-platform content adaptation

### For AI Engineers
- Example of production-ready AI agent architecture
- Pydantic AI implementation with structured outputs
- Hybrid database (SQL + vector) integration
- Containerized deployment with Docker
