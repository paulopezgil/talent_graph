# Global Preferences
- GENERATION: Never generate more than one logical unit at a time.
- DECISIONS: Always explain trade-offs before deciding on a technical approach.
- STYLE: Prefer explicit configuration and code over implicit magic.
- WORKFLOW: Write tests before implementation (TDD).

# Project Specifics
**Project Name**: Mars AI / TalentStream AI
**Description**: RAG-based talent acquisition system. Ingests employee profiles (free-text bio/metadata), extracts structured skills and experience using an LLM, embeds the text into Qdrant vector DB, and allows for natural language semantic search with metadata filters.
**Language & Tooling**: Python 3.x, FastAPI, Streamlit, Qdrant, LangChain, Pytest.
**Conventions**: PEP 8 style, strict typing with Pydantic, modular services.

## Architecture

**IMPORTANT: The architecture that we have planned and want to achieve is inside the `docs/` folder.**

### Current Services
- **`backend/app/services/llm_service/`** — LangChain + OpenAI integration
  - `clients.py` — Module-level singletons: `ChatOpenAI` (gpt-4o-mini) and `OpenAIEmbeddings` (text-embedding-ada-002)
  - `prompts.py` — Prompt templates for profile extraction and query parsing
  - `parse_employee_profile.py` — Async function; extracts skills + experience from bio via LLM structured output
  - `parse_query.py` — Async function; decomposes natural language queries into `ParsedQuery` with filters

- **`backend/app/services/qdrant_service/`** — Vector DB operations
  - `client.py` — Module-level `QdrantClient` singleton
  - `ensure_collection.py` — Creates "employees" collection (1536-dim, cosine) if missing
  - `upsert_employee.py` — Embeds profile text and stores with nested skill metadata
  - `search_employees.py` — Builds nested Qdrant filters (per-skill experience thresholds, department, grade, location, total years) then runs filtered vector search

### Schema (`backend/app/schemas.py`)
Key models: `ParseEmployeeProfilePayload` (input), `ParseEmployeeProfileAIMetadata` (LLM-extracted), `ParseEmployeeProfileAI` (complete parsed profile), `QueryRequest` / `ParsedQuery` (search), `SkillFilter` (per-skill filter with min/max years).

### API (`backend/app/api/v1/endpoints.py`)
- `POST /employees/upload` — Ingest, extract metadata, index
- `POST /query` — Natural language search with metadata filtering
- `GET /health`

### Frontend (`frontend/app.py`)
Streamlit app with two tabs: Upload (profile ingestion) and Search (query interface).

## Build / Lint / Test Commands

### Local Development Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt -r frontend/requirements.txt

# Start Qdrant only
docker compose up qdrant -d
```

### Running Tests
Always run tests from the `backend/` directory so import paths resolve correctly. **Never run test files directly with python3 — always use pytest.**

**Run a Single Test (Crucial for agent debugging)**:
```bash
cd backend
python -m pytest tests/test_parse_employee_profile.py -v
```

**Run a Specific Test Function**:
```bash
cd backend
python -m pytest tests/test_parse_employee_profile.py::test_specific_function -v
```

**Run All Tests**:
```bash
cd backend
python -m pytest tests/ -v
```

### Build & Run
**Docker (Recommended)**:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker compose up --build
```

**Local Backend**:
```bash
# Backend (port 8000) — run from repo root or set PYTHONPATH
cd backend
QDRANT_HOST=localhost OPENAI_API_KEY=sk-... uvicorn main:app --reload --port 8000
```

**Local Frontend**:
```bash
# Frontend (port 8501, separate terminal)
cd frontend
API_URL=http://localhost:8000 streamlit run app.py
```

### Linting & Formatting
While there is no strict linter currently enforced in requirements, the standard expectation is:
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
- Rely heavily on `pydantic` for data validation, parsing, and structured outputs (e.g., LLM structured output schemas).
- Define models in `backend/app/schemas.py`.
- Do not use `Any` unless absolutely unavoidable; strive for strict schema definitions.

### 3. Imports
- Use absolute imports based on the application root (e.g., `from app.api.v1.endpoints import router`).
- Organize imports into 3 distinct blocks, separated by a blank line:
  1. Standard library imports
  2. Third-party dependency imports (FastAPI, Pydantic, etc.)
  3. Local project imports
- Avoid wildcard imports (`from module import *`).

### 4. Naming Conventions
- **Variables & Functions**: `snake_case` (e.g., `parse_employee_profile`)
- **Classes**: `PascalCase` (e.g., `QdrantService`, `EmployeeProfile`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **File Names**: `snake_case` (e.g., `parse_query.py`)
- Name files and functions based on their distinct actions (e.g., `upsert_employee.py` instead of a generic `helpers.py`).

### 5. Error Handling & Logging
- **Do not swallow errors.** Catch specific exceptions rather than broad `Exception` blocks.
- If catching a generic error, ensure it is appropriately logged or re-raised as an `HTTPException` for FastAPI.
- Use structured logging instead of raw `print()` statements where possible.
- Return standard HTTP status codes in FastAPI endpoints.

### 6. Comments & Documentation
- **Docstrings**: Use docstrings for modules, classes, and complex functions. Briefly explain *what* the component does and its inputs/outputs.
- **Inline Comments**: Use them sparingly to explain *why* complex logic is written a certain way. Do not explain *what* the code does if it's already obvious from the code itself.
- Keep the `README.md` and `AGENTS.md` up-to-date with architectural changes.

### 7. Environment Variables
- Manage environment variables via `pydantic-settings` instead of redundant `os.getenv` calls.
- Document new environment variables in the setup guides and `.env.example`.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required |
| `QDRANT_HOST` | `qdrant` | Qdrant hostname |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `API_URL` | `http://backend:8000` | Backend URL (frontend only) |

### 8. Architecture & Structure
- **Backend Services**: Keep logic out of API endpoints. Endpoint files (`api/v1/endpoints.py`) should only handle routing and HTTP lifecycle.
- Delegate core logic to isolated functions in `app/services/`.
- Ensure proper separation of concerns: LLM logic goes in `llm_service`, Vector DB logic goes in `qdrant_service`.

---

## Available Agents
- **Senior Architect**: `.opencode/agents/architect.md` (Helps design software architecture and technical plans)
- **Stepwise Builder**: `.opencode/agents/stepwise-builder.md` (Constructs code incrementally and collaboratively)

## Available Skills
| Task | Skill File Path |
| :--- | :--- |
| Writing tests | `skills/writing-tests.md` |
| Adding a new module | `skills/adding-a-module.md` |
| Publishing package to PyPI | `skills/publishing-to-pypi.md` |

## Current Focus & Known Issues
- Enhance test coverage for edge cases in employee parsing.
- Implement structured logging for LLM calls and Qdrant operations (they are currently silently swallowed or untracked).
- Refactor `config.py` to leverage `pydantic-settings` directly for environment variables.
