# Backend Architecture

## Directory Structure

```text
backend/
├── core/           # Application config, security, and DB connection singletons
├── routers/        # API routing and endpoint definitions
│   ├── agent.py        # Endpoints for interacting with the Pydantic AI agent
│   ├── projects.py     # Endpoints for Project tab
│   ├── messages.py     # Endpoints for Chat tab history
│   ├── scripts.py      # Endpoints for Script tab
│   └── social_media.py # Endpoints for Social Network tab
├── services/       # Core business logic
│   ├── agent.py      # Pydantic AI agent definition and tools
│   └── crud/         # Repository pattern: Reusable DB operations
│       ├── projects.py
│       ├── messages.py
│       ├── scripts.py
│       └── social_media.py
├── models/         # Database ORM models (SQLAlchemy table structures)
├── schemas/        # Pydantic validation schemas (API requests/responses)
└── app.py
```

## Core Concept: Tab-to-Table Mapping

The backend database schema is designed to map explicitly 1:1 with the frontend UI tabs. 

Each tab in the frontend workspace corresponds directly to a database table. FastAPI exposes specific endpoints for each of these tables to allow the frontend to read and update the vertically stacked fields in each tab. 

Crucially, **these exact same update operations are exposed as function tools to the AI Agent**. This ensures that whether a user manually edits a text box in the UI, or the AI agent generates content in execution mode, both go through the exact same data lifecycle.

The mapping is as follows:
1. **Project Tab** → `projects` table (updated via `PUT /projects/{id}`)
2. **Chat Tab** → `messages` table (updated implicitly via chat interaction)
3. **Script Tab** → `scripts` table (updated via `PUT /projects/{id}/script`)
4. **Social Network Tab** → `social_media` table (updated via `PUT /projects/{id}/social-media`)

## Database Schema

### 1. Projects Table (`projects`)
Stores metadata about each project. Mapped to the **Project Tab**.

| Column      | Type        | Description |
|-------------|-------------|-------------|
| id          | UUID (PK)   | Unique project identifier |
| title       | TEXT        | Project title |
| description | TEXT        | Project description |
| created_at  | TIMESTAMPTZ | Timestamp of creation |
| updated_at  | TIMESTAMPTZ | Timestamp of last update |

### 2. Messages Table (`messages`)
Stores chat history for the AI agent per project. Mapped to the **Chat Tab**.

| Column      | Type        | Description |
|-------------|-------------|-------------|
| id          | UUID (PK)   | Unique message identifier |
| project_id  | UUID (FK)   | Links to project |
| role        | TEXT        | `user` or `assistant` |
| content     | TEXT        | Message text |
| created_at  | TIMESTAMPTZ | Timestamp of message |

### 3. Scripts Table (`scripts`)
Stores the generated video scripts. Mapped to the **Script Tab**.

| Column      | Type        | Description |
|-------------|-------------|-------------|
| id          | UUID (PK)   | Unique script identifier |
| project_id  | UUID (FK)   | Links to project (One-to-One or One-to-Many) |
| content     | TEXT        | The script content / sections |
| created_at  | TIMESTAMPTZ | Timestamp of creation |
| updated_at  | TIMESTAMPTZ | Timestamp of last update |

### 4. Social Media Table (`social_media`)
Stores generated captions, descriptions, and hashtags. Mapped to the **Social Network Tab**.

| Column      | Type        | Description |
|-------------|-------------|-------------|
| id          | UUID (PK)   | Unique post identifier |
| project_id  | UUID (FK)   | Links to project (One-to-One or One-to-Many) |
| youtube_title | TEXT      | Auto-generated title for YouTube |
| youtube_description | TEXT | Description/caption |
| instagram_description | TEXT | Instagram caption |
| tiktok_description | TEXT | TikTok caption |
| twitter_post | TEXT       | Twitter post content |
| linkedin_post | TEXT      | LinkedIn post content |
| created_at  | TIMESTAMPTZ | Timestamp of creation |
| updated_at  | TIMESTAMPTZ | Timestamp of last update |

## AI Agent & Context Management

The Agent logic is strictly separated into two layers:

### 1. The Core Agent Service (`services/agent.py`)
- Implemented using **Pydantic AI**. It has no knowledge of HTTP routing.
- **Dependencies (`ProjectAgentDeps`):** A dataclass that provides the `AsyncSession` (database connection) and the `project_id` to the agent's prompts and tools.
- **Dynamic System Prompt:** A function (`@vidplan_agent.system_prompt`) that runs before every LLM call. It fetches the real-time state of the `Project`, `Script`, and `SocialMedia` rows from the DB and injects their content into the system instructions. This turns the database into the Agent's long-term memory.
- **Execution Tools:** Explicit Python functions (`@vidplan_agent.tool`) that allow the AI to execute updates. When called, these functions use the injected DB session to execute SQLAlchemy `UPDATE` queries on the DB, simulating a user clicking "Save" on the frontend tabs:
  - `update_project_tab(ctx, title, description)`
  - `update_script_tab(ctx, content)`
  - `update_social_media_tab(ctx, ...)`
- **Safety:** The AI never writes raw SQL. It outputs validated JSON matching the tool schemas, and the backend executes the explicit updates.

### 2. The HTTP API Router (`routers/agent.py`)
This layer handles the web requests, orchestrates the short-term sliding window memory, and invokes the Core Agent Service.

- **Endpoint 1: `POST /api/projects/{project_id}/agent/chat` (New Message)**
  1. Saves the user's input to the `messages` table.
  2. Fetches a sliding window (e.g., last 10 messages) from the `messages` table to act as short-term memory.
  3. Executes the Pydantic AI agent, passing the memory and dependencies.
  4. Saves the AI's final text response to the `messages` table.
  5. Returns the text response to the frontend.

- **Endpoint 2: `PUT /api/projects/{project_id}/agent/chat/regenerate` (Regenerate Last Message)**
  1. Updates the `content` of the *last* user message with the newly provided text.
  2. Deletes the *last* assistant message from the DB to clean up the timeline.
  3. Fetches the sliding window of messages *prior* to the updated user message.
  4. Executes the Agent exactly as above.
  5. Saves the new AI response to the DB and returns it to the frontend.

## Architecture Patterns

### Repository Pattern (`services/crud/`)
To prevent business logic and database queries from being locked inside HTTP routers, the backend implements the Repository Pattern. 
- **Routers (`routers/`)** are extremely thin. They only handle HTTP requests, validate payloads using Pydantic, call the CRUD service, and return HTTP responses.
- **CRUD Services (`services/crud/`)** contain all the SQLAlchemy `select`, `insert`, and `update` logic. This allows both the FastAPI endpoints AND the AI Agent to reuse the exact same database operations.

## Backend Responsibilities

1. Expose explicit REST endpoints via domain-specific routers (`projects.py`, `messages.py`, `scripts.py`, `social_media.py`) which delegate to `services/crud/`.
2. Receive user messages from the frontend via the `agent.py` router (`POST` for new messages, `PUT` for editing messages).
3. Hydrate context: Fetch the sliding window of `messages` and current state from `projects`, `scripts`, and `social_media` tables using the CRUD service.
4. Call OpenAI API via Pydantic AI (handled in `services/agent.py`).
5. Return response to frontend (validated via schemas in `schemas/`).