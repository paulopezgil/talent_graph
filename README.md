# TalentStream AI

TalentStream AI is a RAG-based talent acquisition system that uses LLM-powered metadata extraction and filtered vector search to match candidates to hiring queries.

## How It Works

1. **Upload** an employee profile (free text bio + optional department/location/grade)
2. An LLM extracts structured metadata: skills (with per-skill experience), total years of experience
3. The profile is embedded and stored in Qdrant alongside its metadata
4. **Search** with natural language (e.g. *"Devs with >5 years experience in Python"*)
5. The query is parsed into metadata filters + a semantic embedding, then Qdrant runs a **metadata-filtered vector search**

## Quick Start

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
docker compose up --build
```

- **Backend API:** http://localhost:8000/docs
- **Frontend UI:** http://localhost:8501
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## Tech Stack

- **FastAPI** — async backend
- **Streamlit** — frontend UI
- **Qdrant** — vector database with nested metadata filtering
- **LangChain + OpenAI** — gpt-4o-mini for extraction, text-embedding-ada-002 for embeddings
- **Docker Compose** — containerized deployment

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. OpenAI API key |
| `QDRANT_HOST` | `qdrant` | Qdrant server hostname |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `API_URL` | `http://backend:8000` | Backend URL (frontend only) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/employees/upload` | Upload an employee profile for LLM extraction and indexing |
| `POST` | `/query` | Natural-language talent search with metadata-filtered vector retrieval |
| `GET` | `/health` | Health check |

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt -r frontend/requirements.txt

# Start Qdrant
docker compose up qdrant -d

# Run backend
cd backend
QDRANT_HOST=localhost OPENAI_API_KEY=sk-... uvicorn main:app --reload --port 8000

# Run frontend (separate terminal)
cd frontend
API_URL=http://localhost:8000 streamlit run app.py
```

## Running Tests

All tests live in `backend/tests/` and must be run from the `backend/` directory so the `app` package is importable.

Because backend settings now validate `OPENAI_API_KEY` at import time, provide that variable when running tests.

Recommended test command (uses a dummy key; external providers are mocked in tests):

```bash
cd backend
OPENAI_API_KEY=test-key python -m pytest tests/ -v
```

If you prefer to use the root `.env` values:

```bash
cd backend
set -a
source ../.env
set +a
python -m pytest tests/ -v
```

Run a single test file:

```bash
cd backend
python -m pytest tests/test_parse_employee_profile.py -v
```

> **Note:** Do not run test files directly with `python3 tests/test_file.py` — this skips the path setup that `pytest` provides and will fail with `ModuleNotFoundError: No module named 'app'`.

### Test Structure

| File | What it covers |
|---|---|
| `tests/test_integration.py` | Full upload → search round-trip through the API (mocked LLM + Qdrant) |
| `tests/test_parse_employee_profile.py` | LLM profile extraction logic |
| `tests/test_parse_query.py` | LLM query parsing logic |
| `tests/test_search_employees.py` | Qdrant search with metadata filtering |

Tests mock external dependencies (OpenAI, Qdrant), so no real API keys or running services are needed. A dummy `OPENAI_API_KEY` is still required for settings initialization.