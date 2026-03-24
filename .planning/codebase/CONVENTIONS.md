# Coding Conventions

**Analysis Date:** 2026-03-24

## Naming Patterns (Planned)

**Files:**
- **Python:** `snake_case.py`.
- **TypeScript:** `kebab-case.ts/tsx`.

**Functions:**
- **Python:** `snake_case`.
- **TypeScript:** `camelCase`.

**Types:**
- **Python (Pydantic):** `PascalCase` (e.g., `UserSchema`).
- **TypeScript:** `PascalCase` (e.g., `UserProps`).

## Code Style (Planned)

**Formatting:**
- **Python:** `ruff` or `black` for formatting.
- **TypeScript:** `prettier` with standard settings (2 spaces, single quotes).

**Linting:**
- **Python:** `ruff check`.
- **TypeScript:** `eslint` with standard React/Next.js rules.

## Import Organization (Planned)

**Order:**
1. Standard library (os, path, etc.).
2. Third-party packages (fastapi, react, next, torch).
3. Internal modules (@/services, @/components).

## Error Handling (Planned)

**Patterns:**
- Use explicit return types (e.g., `Optional[T]` in Python, `T | null` in TypeScript).
- Throw exceptions only for truly exceptional circumstances; use result objects for business logic failures.

## Logging (Planned)

**Framework:**
- **Backend:** Python `logging` with structured JSON output.
- **Frontend:** `console` for dev; integrated logging service for production.

## Comments (Planned)

**When to Comment:**
- Explain "Why", not "What".
- Use docstrings for all public API endpoints and complex services.

---

*Convention analysis: 2026-03-24*
*Initial coding conventions for the virtual try-on platform*
