# Frontend Architecture

## Technology Choice: Streamlit

**Decision**: Use Streamlit instead of React/Next.js for the frontend.
**Rationale**:
- **Rapid prototyping**: Streamlit enables fast iteration on AI application interfaces
- **Python consistency**: Same language as backend reduces context switching
- **Built-in state management**: Session state handles UI state naturally
- **Deployment simplicity**: Single command deployment to Streamlit Cloud
**Trade-off**: Less fine-grained control over UI compared to React, but sufficient for this productivity-focused application.

## UI Structure

### Layout Components

```
┌─────────────────────────────────────────────────────────┐
│                    VidPlan AI Header                    │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│   Left       │             Right Main Panel             │
│   Sidebar    │                                          │
│              │  ┌────────────────────────────────────┐  │
│   • Create   │  │         Tab Navigation             │  │
│     Project  │  ├────────────────────────────────────┤  │
│              │  │                                    |  │
│   • Project  │  │         Tab Content Area           |  │
│     List     │  │   (Project/Chat/Script/Social)     |  │
│              │  │                                    |  │
│              │  └────────────────────────────────────┘  │
└──────────────┴──────────────────────────────────────────┘
```

### 1. Left Sidebar (`frontend/components/sidebar.py`)
- **Project List**: Fetches and displays all projects from `/api/projects`
- **Selection State**: Tracks currently selected project ID in `st.session_state`
- **Create Project Button**: Triggers API call to create new project
- **Auto-refresh**: List updates when new project is created

### 2. Right Main Panel (`frontend/app.py` main content area)
- **Tab Navigation**: Streamlit `st.tabs()` component with four fixed tabs
- **Content Area**: Dynamic content based on selected tab and project

## Tab Implementations

### Project Tab (`frontend/tabs/project_tab.py`)
- **Layout**: Vertical stack of form fields
- **Fields**: Title (text input), Description (text area), Tags (multi-select)
- **Data Binding**: Two-way binding with `projects` table
- **Save Mechanism**: Auto-save on blur or explicit save button

### Chat Tab (`frontend/tabs/chat_tab.py`)
- **Message Display**: Chronological list of user/assistant messages
- **Input Area**: Text input with send button
- **API Integration**: 
  - `POST /api/projects/{id}/messages` for new messages
  - `PUT /api/projects/{id}/messages/last` for regeneration
- **Real-time Updates**: Polling or WebSocket for new AI responses

### Script Tab (`frontend/tabs/script_tab.py`)
- **Editor Interface**: Large text area with syntax highlighting
- **Version History**: Display previous versions (future enhancement)
- **Export Options**: Copy to clipboard, download as text file

### Social Network Tab (`frontend/tabs/social_tab.py`)
- **Platform Sections**: Collapsible sections for each platform (YouTube, Instagram, etc.)
- **Platform-specific UI**: Character counters, hashtag suggestions
- **Batch Operations**: Copy all, regenerate all

## State Management

### Session State (`st.session_state`)
```python
# Core application state
st.session_state.update({
    "selected_project_id": None,  # Currently selected project
    "projects": [],               # Cached project list
    "messages": {},               # Project ID -> message list
    "scripts": {},                # Project ID -> script content
    "social_media": {},           # Project ID -> social media content
})
```

### Data Flow Pattern
1. **Project Selection**: User clicks project in sidebar → `selected_project_id` updated
2. **Tab Navigation**: User switches tabs → fetch relevant data for current project
3. **Data Editing**: User modifies content → API call to update backend
4. **State Sync**: Successful API response → update local session state

## API Integration Layer

### HTTP Client (`frontend/api/client.py`)
- **Base URL Configuration**: Environment-based API endpoint
- **Error Handling**: Graceful degradation on network errors
- **Authentication**: API key or session-based auth (future)
- **Response Caching**: In-memory cache to reduce API calls

### Data Synchronization
- **Optimistic Updates**: UI updates immediately, API call in background
- **Error Recovery**: Retry logic with exponential backoff
- **Conflict Resolution**: Last-write-wins with user notification

### API Endpoint Mapping

| UI Component | Backend Endpoint | Method | Request Body | Response |
|--------------|------------------|--------|--------------|----------|
| Sidebar - Project List | `/api/projects` | GET | — | List[Project] |
| Sidebar - Create Project | `/api/projects` | POST | `{"title": "New Project"}` | Project |
| Project Tab - Title | `/api/projects/{id}` | PUT | `{"title": "..."}` | Project |
| Project Tab - Description | `/api/projects/{id}` | PUT | `{"description": "..."}` | Project |
| Chat Tab - Send Message | `/api/projects/{id}/messages` | POST | `{"content": "..."}` | Message |
| Chat Tab - Edit & Regenerate | `/api/projects/{id}/messages/last` | PUT | `{"content": "..."}` | Message |
| Chat Tab - Get History | `/api/projects/{id}/messages` | GET | — | List[Message] |
| Script Tab - Content | `/api/projects/{id}/script` | GET | — | Script |
| Script Tab - Update | `/api/projects/{id}/script` | PUT | `{"content": "..."}` | Script |
| Social Media Tab - Get | `/api/projects/{id}/social-media` | GET | — | SocialMedia |
| Social Media Tab - Update | `/api/projects/{id}/social-media` | PUT | `{...fields}` | SocialMedia |


## User Experience Patterns

### 1. Progressive Disclosure
- Simple interface for new users
- Advanced controls available via expanders
- Platform-specific options hidden by default

### 2. Responsive Feedback
- Loading spinners during API calls
- Success/error toast notifications
- Auto-save indicators

### 3. Keyboard Shortcuts
- `Ctrl+Enter` to send message
- `Tab` navigation between fields
- `Esc` to cancel edits

## Performance Considerations

### 1. Data Fetching Strategy
- **Lazy Loading**: Only fetch data when tab is activated
- **Polling Interval**: 5-second refresh for chat updates
- **Cache Invalidation**: Clear cache on explicit user actions

### 2. UI Optimization
- **Virtual Scrolling**: For long chat histories
- **Debounced Input**: Auto-save after 1 second of inactivity
- **Component Memoization**: Prevent unnecessary re-renders

## Testing Strategy

### 1. Unit Tests
- **Component Tests**: Isolated tab component testing
- **API Client Tests**: Mock HTTP responses
- **State Management Tests**: Session state transitions

### 2. Integration Tests
- **End-to-End Workflow**: Create project → chat → generate script
- **Error Scenarios**: Network failures, invalid data
- **Cross-tab Synchronization**: Data consistency across tabs

### 3. UI Tests
- **Streamlit Testing**: Using `st-test` framework
- **Visual Regression**: Screenshot comparison for UI changes
- **Accessibility**: Screen reader compatibility checks

## Deployment Considerations

### Streamlit Cloud
- **Automatic Deployment**: Git push triggers redeploy
- **Scaling**: Streamlit handles concurrent users
- **Secrets Management**: Environment variables for API keys

### Custom Deployment
- **Docker Container**: Included in project's docker-compose
- **Reverse Proxy**: Nginx for SSL termination
- **Health Checks**: `/health` endpoint for monitoring