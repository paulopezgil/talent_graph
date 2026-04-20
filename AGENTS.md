# Global Preferences
- GENERATION: Never generate more than one logical unit at a time.
- DECISIONS: Always explain trade-offs before deciding on a technical approach.
- STYLE: Prefer explicit configuration and code over implicit magic.
- WORKFLOW: Write tests before implementation (TDD).

# Project Specifics
**Project Name**: VidPlan AI (Frontend title: TalentStream AI)
**Description**: Intelligent content-creator assistant designed to streamline production. Features an AI agent with Brainstorming and Execution modes. Uses PGVector for semantic search and RAG.
**Language & Tooling**: Python 3.x, FastAPI, React + TypeScript + Vite, PostgreSQL, PGVector, SQLAlchemy, Pytest.
**Conventions**: PEP 8 style, strict typing with Pydantic, modular services.

## Architecture

**IMPORTANT: The architecture we want to achieve is detailed in `docs/`. Any future AI must read `docs/backend_architecture.md` and `docs/frontend_architecture.md` before making structural changes.**

### Directory Structure
- **`backend/core/`** — Application config, security, and DB connection singletons
- **`backend/routers/`** — API routing and endpoint definitions
- **`backend/services/`** — Core business logic (LLM orchestration, DB operations)
- **`backend/models/`** — Database ORM models (SQLAlchemy table structures)
- **`backend/schemas/`** — Pydantic validation schemas (API requests/responses)
- **`backend/app.py`** — Main FastAPI application entrypoint
- **`frontend/`** — React + TypeScript + Vite Application

### Database Schema (PostgreSQL + PGVector)
- Backend uses `asyncpg` and SQLAlchemy ORM.
- **`project_index`**: Vector table for RAG and semantic search (1536-dim vector).
- **`projects`**: Stores project metadata including `summary` and `key_topics` for LLM context
- **`conversation_context`**: Stores AI memory (`user_intent`, `user_preferences`, `conversation_summary`) - NOT for frontend display

### Frontend
- **Framework**: React + TypeScript + Vite (`src/App.tsx`)
- **State**: React Context for global state (selectedProjectId, activeTab), local useState for everything else
- **Styling**: Plain CSS with component-level files
- **HTTP**: Native fetch API (no Axios or other libraries)

## Build / Lint / Test Commands

### Local Development Setup
```bash
# Start Database (PostgreSQL with pgvector)
docker compose up db -d

# Backend Setup
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Application

**Docker (Recommended)**:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker compose up --build
```

**Local Backend**:
```bash
# Runs on port 8000
cd backend
OPENAI_API_KEY=sk-... uvicorn app:app --reload --port 8000
```

**Local Frontend**:
```bash
# Runs React + Vite on port 5173
cd frontend
npm install
npm run dev
```

### Running Tests
Always run tests from the `backend/` directory so import paths resolve correctly. **Never run test files directly with python — always use pytest.**
```bash
cd backend
python -m pytest tests/ -v
```

### Linting & Formatting
- **Formatter**: `black` or `ruff format`
- **Linter**: `ruff check .`
- **Type Checker**: `mypy .`

---

## Code Style Guidelines

### 1. General Principles
- Keep functions small, focused, and pure where possible.
- Avoid module-level state unless absolutely necessary (like singletons for DB clients).
- Use `async`/`await` for I/O bound operations (FastAPI, LLM calls, DB calls).

### 2. Typing & Data Validation
- Enforce strict typing everywhere. Use Python's `typing` module (`List`, `Dict`, `Optional`, `Any`).
- Rely heavily on `pydantic` for data validation, parsing, and structured outputs.
- Define models in `backend/schemas/`.

### 3. Imports
- Use absolute imports based on the application root (e.g., `from backend.models...`).
- Organize imports into 3 distinct blocks separated by a blank line: Standard library, Third-party, Local project.

### 4. Naming Conventions
- **Variables & Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### 5. Error Handling & Logging
- **Do not swallow errors.** Catch specific exceptions rather than broad `Exception` blocks.
- Return standard HTTP status codes in FastAPI endpoints via `HTTPException`.

### 6. Environment Variables
- Manage environment variables via `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@localhost:5432/vidplan` | Postgres connection string |

### 7. Architecture & Structure
- **Backend Services**: Keep logic out of API endpoints. Endpoint files (`routers/`) should only handle routing and HTTP lifecycle.
- Delegate core logic to isolated functions in `services/`.
## Current State vs. Target Architecture

**Current State (Phase 1 Completed)**:
- **Models**: Cleaned up legacy models. Implemented SQLAlchemy models for `Project`, `Script`, and `SocialMedia` with correct relations.
- **Schemas**: Implemented strict Pydantic models for validation (`schemas/`).
- **Routers**: Replaced monolithic `database.py` with domain-specific routers (`projects.py`, `scripts.py`, `social_media.py`) mapped to explicit endpoints.
- **Next Up**: Phase 2 (Conversation Context + Chat API + React Frontend).

**Target Architecture (VidPlan AI)**:
- A content creator assistant.
- **Backend Schema**: `projects` (with summary, key_topics), `conversation_context` (user_intent, user_preferences, conversation_summary), `scripts`, `social_media`.
- **Backend AI**: Pydantic AI agent that reads conversation_context and uses function tools to update `projects`, `scripts`, `social_media`.
- **Frontend**: React + TypeScript + Vite with sidebar + 4 tabs. Chat is session-based (not persisted).

### Current Intent
This project is evolving. We've pivoted from Streamlit to React + Vite for the frontend, and the `messages` table is now a `conversation_context` table that stores AI memory (user_intent, user_preferences, conversation_summary) - not chat history. Chat messages are session-based only.

### Proposed Implementation Order

**Phase 1: Database & Backend Foundations [COMPLETED]**
- [x] **Clean up Models**: Remove the outdated `Message` model.
- [x] **Implement New Models**: Create SQLAlchemy models for `scripts` and `social_media`, and update `Project` with `summary` and `key_topics`.
- [x] **Pydantic Schemas**: Create the corresponding Pydantic schemas in `schemas/`.
- [x] **CRUD Endpoints**: Implement explicit REST routes split by domain.

**Phase 2: Conversation Context & Chat API [IN PROGRESS]**
1. **Create Conversation Context Table**: New SQLAlchemy model for `conversation_context` with `user_intent`, `user_preferences`, `conversation_summary`.
2. **Create Schemas**: Pydantic schemas for conversation context.
3. **Create CRUD Service**: Add `services/crud/conversation_context.py` with get/update functions.
4. **Create Router**: Add `routers/conversation_context.py` with GET/PUT endpoints.
5. **Create Chat Router**: Add `routers/chat.py` with POST `/chat` endpoint that reads context, invokes AI, and returns response.
6. **Update Agent Service**: Modify `services/agent/` to read from `conversation_context` instead of `messages` table.

**Phase 3: React Frontend Build**
7. **Setup Vite + React**: Initialize React + TypeScript + Vite project.
8. **Create Layout**: Sidebar + Main Panel with tab navigation.
9. **Implement API Layer**: `api/client.ts`, `api/projects.ts`, `api/chat.ts`, `api/script.ts`, `api/social.ts`.
10. **Implement Components**: Sidebar, Tabs, Chat, Editor.
11. **Implement State**: React Context for selectedProjectId and activeTab.
12. **Connect to Backend**: Wire up all endpoints.

**Phase 4: Testing & Polish**
13. **Integration Testing**: Run through the full user journey (Create Project -> Chat -> Generate Script -> Generate Social Media -> Manual Edits).

## Testing Strategy & State

Before we write tests for the database, we need a clear testing strategy. Testing database code against a live development database leads to flaky tests and state leakage. 

### Strategy
1. **Isolated Test Database**: We must use a dedicated test database (or transaction rollbacks) for tests to ensure they run in isolation. Given we use PGVector, SQLite in-memory will not suffice. We need a Postgres test container or database.
2. **Pytest Fixtures**: Use `pytest-asyncio` and create a fixture that yields an async database session and rolls back the transaction after each test.
3. **Factory Patterns**: Use factories (e.g., `factory_boy`) or helper functions to generate test data instead of manually building objects in every test.

### Current State
- [x] Database: SQLAlchemy Models implemented.
- [ ] Database Tests: Need CRUD tests for `projects`, `conversation_context`, `scripts`, and `social_media_posts`.
- [ ] Database Tests: Need tests for PGVector similarity search on the `project_index`.
