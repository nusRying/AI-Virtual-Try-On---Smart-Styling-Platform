# Testing Patterns

**Analysis Date:** 2026-03-24

## Test Framework (Planned)

**Backend Runner:**
- `pytest`.
- `httpx` for API testing.

**Frontend Runner:**
- `vitest`.
- `react-testing-library` for component testing.

**Run Commands (Planned):**
```bash
pytest                                # Run all backend tests
npm test                              # Run all frontend tests
```

## Test File Organization (Planned)

**Location:**
- Backend: `backend/tests/`.
- Frontend: `frontend/src/**/*.test.ts/tsx`.

## Mocking (Planned)

**Patterns:**
- Mock AI models for faster unit testing (use `unittest.mock` or `pytest-mock`).
- Mock API responses in frontend tests using `msw` or `vi.fn`.

## Fixtures and Factories (Planned)

**Test Data:**
- Python: `pytest` fixtures for common data (e.g., test images, merchant config).
- TypeScript: Factory functions for creating test data objects.

---

*Testing analysis: 2026-03-24*
*Initial testing plan for the virtual try-on platform*
