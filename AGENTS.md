# Global Preferences
- GENERATION: Never generate more than one logical unit at a time.
- DECISIONS: Always explain trade-offs before deciding on a technical approach.
- STYLE: Prefer explicit configuration and code over implicit magic.
- WORKFLOW: Write tests before implementation (TDD).

# Project Specifics
**Project Name**: VidPlan AI (Frontend title: TalentStream AI)
**Description**: Intelligent content-creator assistant designed to streamline production. Features an AI agent with Brainstorming and Execution modes. Uses PGVector for semantic search and RAG.
**Language & Tooling**: Python 3.x, FastAPI, Streamlit, PostgreSQL, PGVector, SQLAlchemy, Pytest.
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
- **`frontend/`** — Streamlit UI Application

### Database Schema (PostgreSQL + PGVector)
- Backend uses `asyncpg` and SQLAlchemy ORM.
- **`project_index`**: Vector table for RAG and semantic search (1536-dim vector).

### Frontend
- **Framework**: Streamlit (`frontend/app.py`)
- *Note: Previous iterations or plans may have referenced Next.js, but the current implementation is Streamlit.*

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
# Runs Streamlit UI
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
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
- **Models**: Cleaned up legacy models. Implemented SQLAlchemy models for `Project`, `Message`, `Script`, and `SocialMedia` with correct relations.
- **Schemas**: Implemented strict Pydantic models for validation (`schemas/`).
- **Routers**: Replaced monolithic `database.py` with domain-specific routers (`projects.py`, `messages.py`, `scripts.py`, `social_media.py`) mapped to explicit endpoints.
- **Next Up**: Phase 2 (Repository Pattern Refactor & AI Agent Implementation).

**Target Architecture (VidPlan AI)**:
- A content creator assistant.
- **Backend Schema**: `projects`, `messages`, `scripts`, `social_media`.
- **Backend AI**: Pydantic AI agent with brainstorming mode (saves to `messages`) and execution mode (updates `projects`, `scripts`, `social_media` via explicit function calling).
- **Frontend UI**: Left Sidebar (Project selection/creation) and Right Main Panel (Project Tab, Chat Tab, Script Tab, Social Network Tab) mapping 1:1 to the database tables.

### Proposed Implementation Order

**Phase 1: Database & Backend Foundations [COMPLETED]**
- [x] **Clean up Models**: Remove the outdated `Document` and `Tag` models.
- [x] **Implement New Models**: Create SQLAlchemy models for `scripts` and `social_media`, and update `Project` and `Message`.
- [x] **Pydantic Schemas**: Create the corresponding Pydantic schemas in `schemas/`.
- [x] **CRUD Endpoints**: Implement explicit REST routes split by domain.

**Phase 2: AI Agent & Orchestration [IN PROGRESS]**
5. **Repository Pattern Refactor**: Move SQLAlchemy DB queries out of the routers and into `services/crud/` so they can be reused by the Agent tools.
6. **Agent Service**: Build the core Pydantic AI logic in `services/agent.py`. Implement State-Driven memory (injecting DB rows into system prompt) and define function tools (`update_script`, etc.).
7. **Agent Router**: Implement `routers/agent.py` to handle `POST` (New Message) and `PUT` (Regenerate Last Message), fetching short-term sliding window history and invoking the agent.

**Phase 3: Frontend Refactoring (Streamlit)**
7. **Core UI Shell**: Completely rework `frontend/app.py` to remove the old "Talent" tabs. Implement the Left Sidebar for project management (list projects, create new) and the Right Main Panel layout.
8. **Tab Components**: Implement the four specific tabs (`Project`, `Chat`, `Script`, `Social Network`), wiring them up to the Phase 1 CRUD endpoints to display and edit data vertically.
9. **Chat Integration**: Connect the `Chat Tab` to the Phase 2 Agent endpoints, ensuring the UI updates when the AI enters "execution mode" and writes to other tabs.

**Phase 4: Testing & Polish**
10. **Integration Testing**: Run through the full user journey (Create Project -> Chat Brainstorming -> Generate Script -> Generate Social Media -> Manual Edits) to ensure end-to-end functionality.

## Testing Strategy & State

Before we write tests for the database, we need a clear testing strategy. Testing database code against a live development database leads to flaky tests and state leakage. 

### Strategy
1. **Isolated Test Database**: We must use a dedicated test database (or transaction rollbacks) for tests to ensure they run in isolation. Given we use PGVector, SQLite in-memory will not suffice. We need a Postgres test container or database.
2. **Pytest Fixtures**: Use `pytest-asyncio` and create a fixture that yields an async database session and rolls back the transaction after each test.
3. **Factory Patterns**: Use factories (e.g., `factory_boy`) or helper functions to generate test data instead of manually building objects in every test.

### Current State
- [x] Database: SQLAlchemy Models implemented.
- [ ] Database Tests: Need CRUD tests for `projects`, `messages`, `scripts`, and `social_media_posts`.
- [ ] Database Tests: Need tests for PGVector similarity search on the `project_index`.
