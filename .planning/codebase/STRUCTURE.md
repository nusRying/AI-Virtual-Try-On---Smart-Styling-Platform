# Codebase Structure

**Analysis Date:** 2026-03-24

## Directory Layout (Planned)

```
[project-root]/
├── backend/            # FastAPI Backend
│   ├── app/            # Main application logic
│   ├── models/         # AI Model definitions and weights
│   └── tests/          # Backend unit/integration tests
├── frontend/           # Next.js Frontend
│   ├── src/            # React source code
│   └── tests/          # Frontend unit/E2E tests
├── docs/               # Technical documentation
└── .planning/          # GSD planning and state
```

## Directory Purposes (Planned)

**backend/app/**
- Purpose: FastAPI application logic.
- Contains: `main.py` entry point, routers, services, and schemas.
- Key files: `main.py`, `api/v1/endpoints.py`.

**backend/models/**
- Purpose: AI model definitions, loading scripts, and local weight storage.
- Contains: PyTorch/TensorFlow scripts, weights (large files gitignored).

**frontend/src/**
- Purpose: Next.js frontend code.
- Contains: Components, hooks, pages, and styles.

**docs/**
- Purpose: Higher-level architectural and user documentation.

## Key File Locations (Planned)

**Entry Points:**
- `backend/main.py`: Backend entry point.
- `frontend/src/app/page.tsx`: Frontend main page.

**Configuration:**
- `backend/pyproject.toml` or `requirements.txt`: Python dependencies.
- `frontend/package.json`: Frontend dependencies and scripts.

## Naming Conventions (Planned)

**Python (Backend):**
- Files: `snake_case.py`.
- Functions/Variables: `snake_case`.
- Classes: `PascalCase`.

**TypeScript/React (Frontend):**
- Files: `kebab-case.tsx` for components, `camelCase.ts` for hooks/utils.
- Components: `PascalCase`.
- Variables/Functions: `camelCase`.

## Where to Add New Code (Planned)

**New AI Model:**
- Implementation: `backend/models/`.
- Integration: `backend/app/services/`.

**New Frontend Component:**
- Implementation: `frontend/src/components/`.

**New API Endpoint:**
- Definition: `backend/app/api/v1/`.

---

*Structure analysis: 2026-03-24*
*Planned directory structure for the virtual try-on platform*
