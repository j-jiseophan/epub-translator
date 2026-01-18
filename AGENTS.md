# AGENTS.md

This file contains guidelines and commands for agentic coding agents working in this EPUB Translator repository.

## Project Overview

This is a web-based EPUB translation tool that uses local Ollama models for translation. The project consists of:
- **Backend**: Python FastAPI application with async WebSocket support
- **Frontend**: SvelteKit 5.0+ with TypeScript and Tailwind CSS
- **AI Integration**: Local Ollama models for translation

## Development Commands

### Frontend (SvelteKit)
```bash
cd frontend
npm run dev          # Start development server (localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --reload --port 8000  # Start development server
```

### Combined Development
```bash
./start.sh           # Start both backend (8000) and frontend (5173)
```

### Testing
No test framework is currently configured. When adding tests:
- Frontend: Consider Vitest + @testing-library/svelte
- Backend: Consider pytest + pytest-asyncio

## Code Style Guidelines

### Python Backend
- **Imports**: Standard library → third-party → local imports
- **Type Hints**: Use Python 3.11+ union syntax (`str | None`)
- **Data Models**: Use `dataclass` for internal models, `pydantic.BaseModel` for API schemas
- **Async Patterns**: Heavy use of async/await throughout
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes
- **File Organization**: Separate concerns into `api/`, `core/`, `models/` directories

### TypeScript/Svelte Frontend
- **Imports**: ES6 imports with `$lib/` alias for internal modules
- **Type Safety**: Strong TypeScript with interface definitions
- **State Management**: Use Svelte 5 runes (`$state`, `$derived`) and Svelte stores
- **Components**: Single-file Svelte components with `<script lang="ts">`
- **Naming**: `camelCase` for variables/functions, `PascalCase` for components/types
- **Styling**: Tailwind utility classes with conditional formatting

### Error Handling
- **Backend**: Use proper HTTP status codes, return structured error responses
- **Frontend**: Handle API errors gracefully, show user-friendly messages
- **Logging**: Use appropriate logging levels, avoid logging sensitive data

## Architecture Patterns

### Backend
- **WebSocket Communication**: Real-time updates for translation progress
- **Async Job Processing**: Background tasks for long-running translations
- **Clean Separation**: Parsing → Translation → Rebuilding phases
- **Type Safety**: Pydantic schemas for API request/response validation

### Frontend
- **Component-Based**: Modular Svelte components
- **Reactive State**: Svelte stores and runes for state management
- **API Client**: Centralized API client with proper error handling
- **Progress Tracking**: Real-time progress updates via WebSocket

## File Structure Conventions

```
backend/app/
├── main.py              # FastAPI app entry point
├── api/                 # API endpoints and WebSocket handlers
├── core/                # Business logic (translator, parser, etc.)
└── models/              # Pydantic schemas and data models

frontend/src/
├── routes/              # SvelteKit pages and layouts
├── lib/
│   ├── api/            # API client functions
│   ├── stores/         # Svelte stores
│   └── components/     # Reusable Svelte components
```

## Development Workflow

1. **Backend Changes**: Restart FastAPI server after Python code changes
2. **Frontend Changes**: SvelteKit dev server auto-reloads
3. **API Changes**: Update both Pydantic schemas (backend) and TypeScript interfaces (frontend)
4. **New Features**: Follow the existing pattern of API endpoint → frontend component → state management

## Dependencies

### Backend Key Libraries
- `fastapi>=0.115.0` - Web framework
- `ebooklib>=0.18` - EPUB file handling
- `beautifulsoup4>=4.12.0` - HTML parsing
- `httpx>=0.28.0` - Async HTTP client
- `pydantic>=2.10.0` - Data validation

### Frontend Key Libraries
- `svelte>=5.0.0` - UI framework
- `@sveltejs/kit>=2.0.0` - Full-stack framework
- `tailwindcss>=3.4.0` - CSS framework
- `typescript>=5.0.0` - Type safety

## Common Patterns

### API Endpoints
```python
# Use Pydantic for request/response models
@router.post("/translate")
async def translate(request: TranslateRequest) -> TranslateResponse:
    # Implementation
    pass
```

### Frontend API Calls
```typescript
// Use the centralized API client
import { translate } from '$lib/api/client';
const result = await translate(request);
```

### Component Structure
```svelte
<script lang="ts">
  import type { ComponentProps } from './types';
  $state(props = {} as ComponentProps);
</script>

<div class="tailwind-classes">
  <!-- Content -->
</div>
```

## Notes for Agents

- This project uses `uv` for Python package management (check backend/requirements.txt)
- Frontend uses npm, not yarn or pnpm
- WebSocket connections are used for real-time progress updates
- The project handles EPUB file parsing, chunking, translation, and rebuilding
- Always maintain type safety between backend Pydantic schemas and frontend TypeScript interfaces
- Follow async patterns consistently throughout the codebase