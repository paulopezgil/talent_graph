# Frontend Architecture - VidPlan AI

## Overview

The VidPlan AI frontend is a single-page React application that serves as the user interface for an AI-powered content creation workspace. It provides project management, AI-driven chat interactions, script editing, and social media content generation capabilities.

The primary goal is to give content creators a unified workspace where they can manage projects, collaborate with an AI assistant, and generate content for multiple platforms—all driven by a FastAPI backend.

---

## Tech Stack Explanation

### React

React is the industry-standard choice for building user interfaces. Its component-based architecture naturally maps to our UI needs (sidebar, tabs, chat messages). Functional components with hooks keep the code predictable and easy to read.

**Why React**: Every professional frontend job expects React experience. It's well-documented, has a massive ecosystem, and our constraints (no Redux, plain CSS) keep it simple.

### TypeScript

TypeScript adds compile-time type checking that catches bugs before runtime. For a beginner developer, this is invaluable—it provides autocomplete and explicit error messages rather than silent failures.

**Why TypeScript**: The backend already uses Pydantic (strict typing). Using TypeScript creates consistency. A beginner can see exactly what data shapes look like and what API responses should contain.

### Vite

Vite is a modern build tool that offers instant server start and lightning-fast HMR (Hot Module Replacement). It's the standard for React projects today and requires almost no configuration.

**Why Vite**: It works out of the box. No webpack configuration nightmares. The dev experience is fast, which matters for productivity.

### fetch

The native browser Fetch API handles HTTP requests. No Axios, no React Query, no TanStack Query. Just clean, standard JavaScript.

**Why fetch**: For our scale, adding a library is overengineering. The backend has four simple endpoints. fetch does the job with zero dependencies.

### CSS

Plain CSS with component-level files. No Tailwind, no Bootstrap, no UI framework.

**Why plain CSS**: Beginners must understand CSS fundamentals. Tailwind hides too much. Learning plain CSS builds lasting skills. Our app is simple enough that CSS won't become unmaintainable.

---

## High-Level Architecture

The application follows a standard SPA (Single-Page Application) pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                         App Container                           │
├─────────────────┬───────────────────────────────────────────────┤
│                 │                                               │
│   Left          │            Right Main Panel                   │
│   Sidebar       │                                               │
│                 │  ┌─────┬─────┬─────┬─────┐  (Tabs)            │
│   • Project     │  │Project│Chat │Script│Social │              │
│     List        │  └──┬──┴──┬──┴──┬──┴──┬──┘                   │
│                 │     │     │     │     │                       │
│   • Create      │     ▼     ▼     ▼     ▼                       │
│     New         │   [Tab Content Area]                          │
│                 │   (Dynamic based on active tab)               │
└─────────────────┴───────────────────────────────────────────────┘
```

### Core Principles

1. **Single source of truth**: The backend database is the authoritative data store. The frontend fetches data and displays it. No local caching strategies.

2. **Sidebar + Tab system**: The left sidebar handles project selection. The right panel contains four tabs that switch views. Only one tab visible at a time.

3. **Chat as control surface**: The Chat tab is where users interact with the AI. The AI can read/write to other tabs (scripts, social media) via backend function calls. The chat is the "control center."

---

## Folder Structure

Keep it flat. No deep nesting. Each folder has one clear purpose.

```
src/
├── api/
│   ├── client.ts          # Base fetch wrapper with error handling
│   ├── projects.ts        # Project CRUD operations
│   ├── chat.ts            # Chat message sending (session-based)
│   ├── script.ts          # Script get/update
│   └── social.ts          # Social media get/update
│
├── components/
│   ├── Sidebar.tsx        # Project list + create button
│   ├── Tabs.tsx           # Tab navigation component
│   ├── Chat.tsx           # Chat message list + input
│   ├── Editor.tsx         # Reusable textarea for scripts/social
│   └── Layout.tsx        # Sidebar + main panel wrapper
│
├── pages/
│   └── App.tsx            # Main application component (routes)
│
├── styles/
│   ├── global.css         # Reset, base typography, variables
│   ├── Layout.css         # Sidebar + panel layout
│   ├── Sidebar.css        # Project list styling
│   ├── Tabs.css           # Tab buttons styling
│   ├── Chat.css           # Chat messages + input
│   └── Editor.css         # Textarea styling
│
├── types/
│   └── index.ts           # TypeScript interfaces for all API responses
│
├── main.tsx               # React entry point
└── App.tsx                # Root component (single page, no routing needed)
```

**Why this structure**:

- `api/` groups all HTTP calls in one place—easy to find when debugging
- `components/` contains reusable UI pieces
- `pages/` is minimal because this is a single-view app (not a multi-page site)
- `styles/` is flat with one CSS file per major component
- `types/` centralizes all TypeScript interfaces

---

## State Management Strategy

Keep state minimal. Only two pieces of global state exist.

### Core State (React Context)

```typescript
// types/index.ts
interface AppState {
  selectedProjectId: number | null;
  activeTab: 'project' | 'chat' | 'script' | 'social';
}

// Use a simple Context for these two values
const AppContext = createContext<{
  state: AppState;
  setState: React.Dispatch<SetStateAction<AppState>>;
}>(null);
```

### Why Only This?

1. **selectedProjectId**: Needed everywhere—sidebar shows it, tabs fetch data for it, chat messages belong to it. Must be global.

2. **activeTab**: Controls which view renders. Must be global to persist when switching projects.

### Everything Else Is Local

- Chat messages: Stored in local `useState` (session-based, not persisted)
- Script content: Fetched in `Editor.tsx` (script mode), stored locally
- Social media content: Fetched in `Editor.tsx` (social mode), stored locally

### Session-Based Chat Messages (IMPORTANT)

Chat messages are **not persisted** to the database. They exist only in the current browser session.

**Why**:
- Simpler user experience - users can experiment with the AI without worrying about cluttering their project history
- Faster development - no need to implement message editing/ deletion UI
- The backend `conversation_context` table stores AI memory (user_intent, user_preferences, conversation_summary) - not frontend display data

**How it works**:
```
User sends message
        │
        ▼
Frontend stores message in local useState (UI only)
        │
        ▼
POST /api/projects/{id}/chat with { content: "..." }
        │
        ▼
Backend reads conversation_context (user_intent, user_preferences, conversation_summary)
        │
        ▼
Backend invokes AI with context + user message
        │
        ▼
Backend updates conversation_summary based on interaction
        │
        ▼
Backend returns AI response
        │
        ▼
Frontend displays response in local useState
        │
        ▼
User closes browser → messages lost (but conversation_summary persisted)
```

**Implications**:
- When switching projects, chat clears automatically
- When refreshing the page, chat clears (no persistence)
- The backend maintains conversation context via the database table, but the frontend just shows the current session

---

## Data Flow

### 1. Project Selection Flow

```
User clicks project in sidebar
        │
        ▼
setSelectedProjectId(project.id)
        │
        ▼
Sidebar highlights selected project
        │
        ▼
All tabs now display/fetch data for this project
```

### 2. Tab Switching Flow

```
User clicks tab button (Project/Chat/Script/Social)
        │
        ▼
setActiveTab(tabName)
        │
        ▼
Component for that tab renders
        │
        ▼
useEffect triggers: fetch data for selectedProjectId
        │
        ▼
Display fetched data in UI
```

### 3. Chat Message Flow

```
User types message → presses Enter
        │
        ▼
POST /api/projects/{id}/chat with { content: "..." }
        │
        ▼
Backend reads conversation_context (for AI memory)
        │
        ▼
Backend invokes AI agent
        │
        ▼
Backend updates conversation_summary
        │
        ▼
Backend returns AI response
        │
        ▼
Chat component appends message to local state
        │
        ▼
If AI wrote to script/social: UI prompts to refresh those tabs
```

### 4. UI Update After Backend Changes

```
User edits script → clicks Save
        │
        ▼
PUT /api/projects/{id}/script with { content: "..." }
        │
        ▼
Backend updates database → returns 200 OK
        │
        ▼
UI shows "Saved" confirmation
        │
        ▼
No complex state sync needed—backend is source of truth
```

---

## API Layer Design

### api/client.ts (Base Wrapper)

```typescript
const API_BASE = '/api';

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
```

### api/projects.ts

```typescript
import { fetchApi } from './client';

export interface Project {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

export async function getProjects(): Promise<Project[]> {
  return fetchApi<Project[]>('/projects');
}

export async function createProject(title: string): Promise<Project> {
  return fetchApi<Project[]>('/projects', {
    method: 'POST',
    body: JSON.stringify({ title }),
  }).then(res => res[0]); // API returns array, take first item
}

export async function updateProject(id: number, data: Partial<Project>): Promise<Project> {
  return fetchApi<Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
```

### api/chat.ts

```typescript
import { fetchApi } from './client';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Chat messages are session-based only (see State Management section)
// We send user message, receive AI response - no persistent history

export async function sendChatMessage(projectId: number, content: string): Promise<ChatMessage> {
  return fetchApi<ChatMessage>(`/projects/${id}/chat`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}
```

### api/script.ts

```typescript
import { fetchApi } from './client';

export interface Script {
  id: number;
  project_id: number;
  content: string;
}

export async function getScript(projectId: number): Promise<Script> {
  return fetchApi<Script>(`/projects/${projectId}/script`);
}

export async function updateScript(projectId: number, content: string): Promise<Script> {
  return fetchApi<Script>(`/projects/${projectId}/script`, {
    method: 'PUT',
    body: JSON.stringify({ content }),
  });
}
```

### api/social.ts

```typescript
import { fetchApi } from './client';

export interface SocialMedia {
  id: number;
  project_id: number;
  youtube: string;
  instagram: string;
  twitter: string;
}

export async function getSocialMedia(projectId: number): Promise<SocialMedia> {
  return fetchApi<SocialMedia>(`/projects/${projectId}/social-media`);
}

export async function updateSocialMedia(projectId: number, data: Partial<SocialMedia>): Promise<SocialMedia> {
  return fetchApi<SocialMedia>(`/projects/${projectId}/social-media`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
```

---

## Component Architecture

### Layout.tsx

```typescript
// Wraps sidebar + main panel
// Provides AppContext (selectedProjectId, activeTab)
// CSS: flexbox, sidebar fixed width, main panel grows
```

### Sidebar.tsx

```typescript
// Props: none (consumes AppContext)
// State: local `projects` array (fetched on mount)
// - Fetches all projects on mount
// - Renders list with click handlers to setSelectedProjectId
// - "Create Project" button at bottom
```

### Tabs.tsx

```typescript
// Props: none (consumes AppContext)
// Renders 4 buttons: Project | Chat | Script | Social
// Active tab highlighted based on activeTab state
// Clicking sets activeTab
```

### Chat.tsx

```typescript
// Props: projectId (from AppContext)
// State: local `messages` array (session-based), `input` string, `isLoading` boolean
// - Messages are session-based only (not fetched from backend)
// - User types message → presses Enter → sendMessage to API
// - Display both user message and AI response in local state
// - When project changes → messages reset to empty array
```

### Editor.tsx (Reusable)

```typescript
// Props: 
//   - mode: 'script' | 'social'
//   - projectId: number
// State: local `content` string, `isSaving` boolean
// - Fetches existing content on mount
// - Textarea with content
// - Save button triggers PUT to appropriate endpoint
// - Social mode shows separate fields for each platform
```

---

## Styling Approach

### Global Styles (global.css)

```css
:root {
  --sidebar-width: 250px;
  --primary-color: #2563eb;
  --text-color: #1f2937;
  --bg-color: #ffffff;
  --border-color: #e5e7eb;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-color);
  background: var(--bg-color);
}
```

### Component CSS Files

Each component in `components/` has a matching file in `styles/`:

- `Sidebar.css` — project list styling, hover states
- `Tabs.css` — tab buttons, active indicator
- `Chat.css` — message bubbles, input field, send button
- `Editor.css` — textarea sizing, labels
- `Layout.css` — flex container, sidebar/main split

### Layout Approach

Use CSS Flexbox for the main layout:

```css
.app-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}
```

---

## Build Strategy (3-Day Plan)

### Day 1: Project Setup + Layout

**Morning**:
- Initialize Vite + React + TypeScript project
- Install dependencies (none needed beyond React)
- Create folder structure

**Afternoon**:
- Build `Layout.tsx` with sidebar + main panel
- Create `global.css` with base styles
- Implement `Sidebar.tsx` with static project list (mock data initially)
- Verify layout renders correctly

**Deliverable**: Empty shell app with working sidebar and panel layout.

### Day 2: Tabs + API Integration

**Morning**:
- Implement `Tabs.tsx` with tab switching logic
- Add `AppContext` for global state (selectedProjectId, activeTab)

**Afternoon**:
- Build `api/client.ts` and endpoint files
- Connect `Sidebar.tsx` to real API (getProjects, createProject)
- Implement project selection (click project → update context)
- Verify data loads when project selected

**Deliverable**: Working project list, tab navigation, project switching.

### Day 3: Chat + Editors + Polish

**Morning**:
- Build `Chat.tsx` with message display and input
- Connect to `sendMessage` API
- Handle loading state during API calls

**Afternoon**:
- Build `Editor.tsx` for Script tab
- Build `Editor.tsx` for Social Media tab (with platform fields)
- Add save buttons and API calls
- Basic styling pass (colors, spacing, buttons)
- Test the full user flow: create project → chat → save script

**Deliverable**: Fully functional app with all four tabs working.

---

## Anti-Patterns to Avoid

### 1. Overusing Global State

Don't put everything in Context. Only `selectedProjectId` and `activeTab` need to be global. Everything else should be local to the component that uses it.

**Bad**: Storing messages, scripts, social content all in a global store.

**Good**: Each tab fetches and manages its own data.

### 2. Creating Too Many Abstractions

Don't build "utility" files, "helper" folders, or "service" layers that don't exist yet. Write the simplest thing that works.

**Bad**: Creating a `useFetch` hook, an `apiClient` class, and a `queryProvider` before writing actual API calls.

**Good**: Direct function calls in components. Refactor when repetition appears.

### 3. Premature Optimization

Don't add loading skeletons, error boundaries, or optimistic updates until you actually need them.

**Bad**: Building a complex caching system for API responses.

**Good**: Fetch on mount, show simple "Loading..." text if needed.

### 4. Overengineering Folder Structure

Don't create folders like `hooks/`, `utils/`, `services/`, `contexts/` unless they contain actual files. A flat structure is better than an empty deep structure.

**Bad**: `src/hooks/useCustom.ts`, `src/utils/format.ts` with one function each.

**Good**: Everything in `components/` or directly in `api/`.

### 5. Introducing Redux or Complex Libraries

Redux is overkill for a 4-tab app. TanStack Query is overkill for 4 endpoints. Keep dependencies at zero.

**Bad**: Installing @reduxjs/toolkit, react-router-dom, axios, tailwindcss.

**Good**: Just React. That's enough.

---

## Implementation Notes

### API Routes (from Backend)

| Frontend Need | Backend Endpoint |
|---------------|-------------------|
| List projects | GET `/api/projects` |
| Create project | POST `/api/projects` |
| Send chat message | POST `/api/projects/{id}/chat` |
| Get script | GET `/api/projects/{id}/script` |
| Update script | PUT `/api/projects/{id}/script` |
| Get social | GET `/api/projects/{id}/social-media` |
| Update social | PUT `/api/projects/{id}/social-media` |

**Note**: Chat message history is **not** fetched from the backend. Messages are session-based only.

### Quick Start

```bash
# Create Vite project
npm create vite@latest frontend -- --template react-ts

# Start dev server
cd frontend
npm install
npm run dev
```

The frontend runs on port 5173 by default. Configure Vite to proxy API requests to the backend at port 8000.

---

## Summary

This frontend is intentionally simple. Two global state values. Four API files. Six components. Four CSS files. A beginner can understand the entire codebase in an afternoon.

The architecture prioritizes:
- **Speed**: Build it in 3 days
- **Maintainability**: No complex patterns to learn
- **Learning**: Vanilla React, TypeScript, CSS—transferable skills

Ship fast, learn fast, iterate fast.