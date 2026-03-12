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
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker compose up --build
```

- **Backend API:** http://localhost:8000/docs
- **Frontend UI:** http://localhost:8501
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

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

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/employees/upload` | Upload an employee profile for LLM extraction and indexing |
| `POST` | `/query` | Natural-language talent search with metadata-filtered vector retrieval |
| `GET` | `/health` | Health check |

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
