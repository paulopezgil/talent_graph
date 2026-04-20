# Backend Architecture

## Directory Structure

```text
backend/
├── core/              # Application config, security, and DB connection singletons
├── routers/           # API routing and endpoint definitions
│   ├── projects.py     # Endpoints for Project tab
│   ├── conversation_context.py # Endpoints for LLM context (not frontend-facing)
│   ├── scripts.py      # Endpoints for Script tab
│   └── social_media.py # Endpoints for Social Network tab
├── services/          # Core business logic
│   ├── agent/          # Pydantic AI agent definition, tools, and prompts
│   │   ├── agent.py    # Core Agent definition
│   │   ├── utils.py    # Message history builder
│   │   ├── prompts.py  # System prompts
│   │   └── tools/      # Agent tool definitions
│   │       ├── project.py
│   │       ├── script.py
│   │       └── social_media.py
│   ├── conversation/   # Orchestration layer for agent interactions
│   │   ├── get_agent_response.py  # Handles agent calls and message saving
│   │   └── delete_last_exchange.py # Handles message editing
│   └── crud/          # Repository pattern: Reusable DB operations
│       ├── projects.py
│       ├── conversation_context.py
│       ├── scripts.py
│       └── social_media.py
├── models/            # Database ORM models (SQLAlchemy table structures)
├── schemas/           # Pydantic validation schemas (API requests/responses)
└── app.py
```

## Core Concept: Tab-to-Table Mapping

The backend database schema is designed to map explicitly 1:1 with the frontend UI tabs. 

Each tab in the frontend workspace corresponds directly to a database table. FastAPI exposes specific endpoints for each of these tables to allow the frontend to read and update the vertically stacked fields in each tab. 

Crucially, **these exact same update operations are exposed as function tools to the AI Agent**. This ensures that whether a user manually edits a text box in the UI, or the AI agent generates content in execution mode, both go through the exact same data lifecycle.

The mapping is as follows:
1. **Project Tab** → `projects` table (updated via `PUT /projects/{id}`)
2. **Chat Tab** → Session-based (messages stored only in frontend React state)
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

### 2. Project Table (`projects`)
Stores metadata about each project. Mapped to the **Project Tab**.

| Column      | Type        | Description |
|-------------|-------------|-------------|
| id          | UUID (PK)   | Unique project identifier |
| title       | TEXT        | Project title |
| description | TEXT        | Project description |
| summary     | TEXT        | Brief project summary for quick reference |
| key_topics  | TEXT[]      | Main topics/themes for content generation |
| created_at  | TIMESTAMPTZ | Timestamp of creation |
| updated_at  | TIMESTAMPTZ | Timestamp of last update |

### 3. Conversation Context Table (`conversation_context`)
Stores structured context for the AI agent per project. This table serves as the AI's memory - the backend reads these values to provide context to the LLM during conversations. **Not intended for frontend display**.

| Column             | Type        | Description |
|--------------------|-------------|-------------|
| id                 | UUID (PK)   | Unique identifier |
| project_id         | UUID (FK)   | Links to project |
| user_intent        | TEXT        | What the user is trying to achieve |
| user_preferences   | JSONB       | Style, tone, and content preferences |
| conversation_summary | TEXT     | Brief summary of past AI interactions |
| created_at         | TIMESTAMPTZ | Timestamp of creation |
| updated_at         | TIMESTAMPTZ | Timestamp of last update |

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

The Agent logic is strictly separated into multiple layers:

### 1. The Core Agent Service (`services/agent/`)
- **Agent Definition** (`agent.py`): Implemented using **Pydantic AI**. It has no knowledge of HTTP routing.
- **Dependencies** (`ProjectAgentDeps`): A dataclass that provides the `AsyncSession` (database connection) and the `project_id` to the agent's prompts and tools.
- **Dynamic System Prompt** (`prompts.py`): A function (`@vidplan_agent.system_prompt`) that runs before every LLM call. It fetches the real-time state of the `Project`, `Script`, and `SocialMedia` rows from the DB and injects their content into the system instructions. This turns the database into the Agent's long-term memory.
- **Message History Builder** (`utils.py`): Converts database `Message` rows into Pydantic AI's `ModelMessage` format for conversation continuity.
- **Execution Tools** (`tools/`): Explicit Python functions (`@vidplan_agent.tool`) organized by domain that allow the AI to execute updates:
  - `tools/project.py`: `update_project_tab(ctx, title, description)`
  - `tools/script.py`: `update_script_tab(ctx, content)`
  - `tools/social_media.py`: `update_social_media_tab(ctx, ...)`
- **Safety**: The AI never writes raw SQL. It outputs validated JSON matching the tool schemas, and the backend executes the explicit updates.

### 2. The Conversation Orchestration Layer (`services/conversation/`)
- **get_agent_response.py**: Orchestrates the agent call. Reads conversation context from the database, invokes the agent, updates the conversation summary, returns the response to frontend.
- **update_context.py**: Updates conversation context fields (user_intent, user_preferences, conversation_summary) after interactions.

### 3. The HTTP API Router (`routers/conversation_context.py`)
This router handles LLM context operations. **It is not for frontend display** - the frontend uses session-based messages only.

- **`GET /api/projects/{project_id}/conversation_context`**
  Returns the conversation context (user_intent, user_preferences, conversation_summary) for the AI.

- **`PUT /api/projects/{project_id}/conversation_context`**
  Updates conversation context fields based on user interactions.

## Architecture Patterns

### Repository Pattern (`services/crud/`)
To prevent business logic and database queries from being locked inside HTTP routers, the backend implements the Repository Pattern. 
- **Routers (`routers/`)** are extremely thin. They only handle HTTP requests, validate payloads using Pydantic, call the CRUD service, and return HTTP responses.
- **CRUD Services (`services/crud/`)** contain all the SQLAlchemy `select`, `insert`, and `update` logic. This allows both the FastAPI endpoints AND the AI Agent to reuse the exact same database operations.

### Exception Handling Pattern (`backend/exceptions/`)
The backend implements a centralized exception handling system that ensures consistent error responses across all endpoints.

#### Exception Hierarchy
```
VidPlanError (base)
├── NotFoundError      # Resource not found (404)
├── AgentError         # LLM/AI call failures (500)
├── DatabaseError      # SQLAlchemy operation failures (500)
├── ValidationError    # Data validation failures (400)
└── UnauthorizedError  # Access control failures (401)
```

#### Handler Implementation (`exceptions/handlers.py`)
- **Base Handler** (`handle_vidplan_exception`): Core logic shared by all handlers. Returns an `ErrorResponse` schema with `error_code`, `message`, and optional `detail`.
- **Dev Mode**: When `ENV=development`, includes the full exception `detail` in responses. In production, only returns the public-facing `message`.
- **Specific Handlers**: Each exception type has a dedicated handler that delegates to the base handler with the appropriate HTTP status code.

#### FastAPI Integration (`app.py`)
All exception handlers are registered globally with FastAPI via `app.add_exception_handler()`, ensuring any unhandled exception flows through the centralized error response format.

#### Raising Exceptions in Services
The service layer should raise specific exceptions rather than returning error strings or `None`:
- **CRUD Layer** (`services/crud/`): Raise `NotFoundError` when resources don't exist, wrap commit failures in `DatabaseError`
- **Agent Layer** (`services/agent/`): Wrap LLM call failures in `AgentError`
- **Conversation Layer** (`services/conversation/`): Propagate exceptions from underlying layers

## Backend Responsibilities

1. Expose explicit REST endpoints via domain-specific routers (`projects.py`, `scripts.py`, `social_media.py`) which delegate to `services/crud/`.
2. Chat messages are handled via session-based communication - frontend sends user message, backend processes and returns AI response.
3. Maintain conversation context: Read from `conversation_context` table and inject into LLM prompts.
4. Call OpenAI API via Pydantic AI (handled in `services/agent.py`).
5. Return response to frontend (validated via schemas in `schemas/`).

## Design Decisions & Trade-offs

### 1. Database as Memory Pattern
**Decision**: Store all project state in PostgreSQL rather than in-memory session storage.
**Rationale**: 
- Enables persistence across server restarts and user sessions
- Allows for historical analysis and versioning
- Simplifies deployment (no Redis or external cache required)
**Trade-off**: Slightly higher database load, but PostgreSQL handles this well for moderate traffic.

### 2. Tab-to-Table Explicit Mapping
**Decision**: Each UI tab corresponds directly to a database table with explicit CRUD endpoints.
**Rationale**:
- Clear mental model for developers (what you see is what's stored)
- Enables both manual editing and AI generation through the same interface
- Simplifies permissioning and audit trails
**Trade-off**: Less flexible than document storage but provides stronger data consistency.

### 3. Repository Pattern Implementation
**Decision**: Separate data access layer (`services/crud/`) from HTTP layer (`routers/`).
**Rationale**:
- Enables reuse by both REST API and AI agent tools
- Centralizes database logic for easier testing and maintenance
- Follows Single Responsibility Principle
**Trade-off**: Slight increase in code complexity but significant improvement in testability.

### 4. Pydantic AI for Structured Outputs
**Decision**: Use Pydantic AI instead of raw OpenAI function calling.
**Rationale**:
- Type-safe tool definitions with automatic validation
- Built-in retry logic and error handling
- Clean separation between tool definitions and implementation
**Trade-off**: Additional dependency but provides production-ready reliability.

## Scalability Considerations

### Current Architecture (Suitable for 1-100 concurrent users)
- **Database**: Single PostgreSQL instance with PGVector
- **Backend**: Single FastAPI instance (stateless, can be scaled horizontally)
- **AI Calls**: Direct to OpenAI/other providers (rate-limited by provider)

### Scaling Path
1. **Horizontal Scaling**: Add more FastAPI instances behind a load balancer
2. **Database**: Implement read replicas for `GET` endpoints
3. **Vector Search**: Consider dedicated vector DB (Qdrant, Pinecone) for larger datasets
4. **Caching**: Add Redis for frequently accessed project data
5. **Async Processing**: Move AI generation to background tasks for longer operations

## Testing Strategy

### Unit Tests
- **CRUD Operations**: Test each repository function in isolation
- **Pydantic Schemas**: Validate data models and transformations
- **Agent Tools**: Test tool functions with mocked database sessions

### Integration Tests
- **API Endpoints**: Test full HTTP request/response cycle
- **Database Operations**: Test with test database using transaction rollbacks
- **AI Integration**: Test with mocked LLM responses

### Test Fixtures
- Use `pytest-asyncio` for async test support
- Database fixtures create test data and clean up after each test
- Factory patterns for generating test entities

## Security Considerations

### 1. API Security
- **Input Validation**: All endpoints use Pydantic schemas for strict validation
- **CORS**: Configured for frontend domain only
- **Rate Limiting**: Implemented at the load balancer level

### 2. Data Security
- **Project Isolation**: Users can only access their own projects (future enhancement)
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **API Keys**: Environment variables with secrets management

### 3. AI Safety
- **Tool Validation**: Pydantic ensures structured outputs before execution
- **Content Filtering**: Provider-level content moderation
- **Audit Trail**: All AI-generated content stored with timestamps and context