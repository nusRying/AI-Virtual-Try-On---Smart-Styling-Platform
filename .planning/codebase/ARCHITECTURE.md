# Architecture

**Analysis Date:** 2026-03-24

## Pattern Overview

**Overall:** AI-Powered B2B SaaS Platform (Planned)

**Key Characteristics:**
- **Microservices-ready Monolith:** Python (FastAPI) backend for core logic and AI orchestration.
- **Modern Frontend:** Next.js (React) for the styling dashboard and merchant plugin.
- **AI-Centric:** Heavy reliance on PyTorch for virtual try-on and recommendation models.
- **API-First:** Designed to be embedded via plugin or consumed via API by e-commerce stores.

## Layers (Planned)

**Frontend Layer (Next.js):**
- Purpose: User interface for try-on, styling, and merchant analytics.
- Contains: React components, styling logic, API client.
- Depends on: Backend API.
- Used by: End-users, E-commerce merchants.

**API Layer (FastAPI):**
- Purpose: Orchestrate requests, handle authentication, and interface with AI models.
- Contains: Route handlers, request validation, business logic.
- Depends on: Model Inference Layer, Database.
- Used by: Frontend, External API consumers.

**Model Inference Layer (PyTorch):**
- Purpose: Run CV and Generative AI models for try-on and styling.
- Contains: Pose estimation, segmentation, diffusion models.
- Depends on: GPU infrastructure, Model weights.
- Used by: API Layer.

**Data Layer:**
- Purpose: Persist user preferences, clothing metadata, and analytics.
- Contains: Database schemas, repository patterns.
- Depends on: PostgreSQL/NoSQL.
- Used by: API Layer.

## Data Flow (Planned)

**Virtual Try-On Flow:**

1. User/Merchant uploads image via Frontend.
2. API Layer receives image and stores it in temporary/permanent storage.
3. API Layer triggers Model Inference Layer.
4. Model Inference performs:
   - Pose detection (MediaPipe)
   - Segmentation
   - Virtual Try-On (Diffusion model)
5. Resulting image/data is returned to API Layer.
6. API Layer returns result to Frontend for display.

**State Management:**
- **Client-side:** React State/Context for interactive try-on sessions.
- **Server-side:** Stateless API with database persistence for long-term data.

## Key Abstractions (Planned)

**TryOnEngine:**
- Purpose: Abstract the complexity of different AI models for try-on.
- Pattern: Strategy Pattern (support multiple model versions).

**StylistService:**
- Purpose: Logic for generating outfit recommendations.
- Pattern: Service Layer.

## Entry Points

**Backend:** `backend/main.py` (Planned FastAPI entry)
**Frontend:** `frontend/src/app/page.tsx` (Planned Next.js entry)

## Error Handling (Planned)

**Strategy:** Centralized error middleware in FastAPI to return consistent JSON responses.

**Patterns:**
- Custom exception classes for domain-specific errors (e.g., `InferenceError`, `ValidationError`).
- Fail-fast validation at the API boundary using Pydantic.

## Cross-Cutting Concerns (Planned)

**Logging:**
- Structured logging (JSON) for easy analysis of inference performance and errors.

**Validation:**
- Pydantic for API request/response validation.
- Image quality/format validation before processing.

**Authentication:**
- JWT-based auth for merchants and B2C users.

---

*Architecture analysis: 2026-03-24*
*Initial setup based on project vision*
