<!-- GSD:project-start source:PROJECT.md -->
## Project

**AI Virtual Try-On + Smart Styling Platform**
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python - Planned for Backend and AI model implementation.
- TypeScript/JavaScript - Planned for Frontend (React/Next.js).
- Not detected
## Runtime
- Python (likely 3.10+) - Required for PyTorch and FastAPI.
- Node.js - Required for Next.js/React development and execution.
- pip/poetry (Planned)
- npm/yarn/pnpm (Planned)
- Lockfile: missing
## Frameworks
- FastAPI - Planned backend framework.
- Next.js / React - Planned frontend framework.
- PyTorch - Primary framework for AI models.
- Not detected
- Docker/Containers - Mentioned for infrastructure.
## Key Dependencies
- `pytorch` - For AI model training and inference.
- `fastapi` - For building the API.
- `next` - For the web application.
- AI Models (Planned):
## Configuration
- Not yet configured.
- Likely requires GPU-enabled environment variables and API keys for cloud services.
- Not detected
## Platform Requirements
- Python 3.x
- Node.js
- GPU support for local model testing (optional)
- GPU Instances (AWS / GCP)
- Cloud Run or other container orchestration platforms.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns (Planned)
- **Python:** `snake_case.py`.
- **TypeScript:** `kebab-case.ts/tsx`.
- **Python:** `snake_case`.
- **TypeScript:** `camelCase`.
- **Python (Pydantic):** `PascalCase` (e.g., `UserSchema`).
- **TypeScript:** `PascalCase` (e.g., `UserProps`).
## Code Style (Planned)
- **Python:** `ruff` or `black` for formatting.
- **TypeScript:** `prettier` with standard settings (2 spaces, single quotes).
- **Python:** `ruff check`.
- **TypeScript:** `eslint` with standard React/Next.js rules.
## Import Organization (Planned)
## Error Handling (Planned)
- Use explicit return types (e.g., `Optional[T]` in Python, `T | null` in TypeScript).
- Throw exceptions only for truly exceptional circumstances; use result objects for business logic failures.
## Logging (Planned)
- **Backend:** Python `logging` with structured JSON output.
- **Frontend:** `console` for dev; integrated logging service for production.
## Comments (Planned)
- Explain "Why", not "What".
- Use docstrings for all public API endpoints and complex services.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- **Microservices-ready Monolith:** Python (FastAPI) backend for core logic and AI orchestration.
- **Modern Frontend:** Next.js (React) for the styling dashboard and merchant plugin.
- **AI-Centric:** Heavy reliance on PyTorch for virtual try-on and recommendation models.
- **API-First:** Designed to be embedded via plugin or consumed via API by e-commerce stores.
## Layers (Planned)
- Purpose: User interface for try-on, styling, and merchant analytics.
- Contains: React components, styling logic, API client.
- Depends on: Backend API.
- Used by: End-users, E-commerce merchants.
- Purpose: Orchestrate requests, handle authentication, and interface with AI models.
- Contains: Route handlers, request validation, business logic.
- Depends on: Model Inference Layer, Database.
- Used by: Frontend, External API consumers.
- Purpose: Run CV and Generative AI models for try-on and styling.
- Contains: Pose estimation, segmentation, diffusion models.
- Depends on: GPU infrastructure, Model weights.
- Used by: API Layer.
- Purpose: Persist user preferences, clothing metadata, and analytics.
- Contains: Database schemas, repository patterns.
- Depends on: PostgreSQL/NoSQL.
- Used by: API Layer.
## Data Flow (Planned)
- **Client-side:** React State/Context for interactive try-on sessions.
- **Server-side:** Stateless API with database persistence for long-term data.
## Key Abstractions (Planned)
- Purpose: Abstract the complexity of different AI models for try-on.
- Pattern: Strategy Pattern (support multiple model versions).
- Purpose: Logic for generating outfit recommendations.
- Pattern: Service Layer.
## Entry Points
## Error Handling (Planned)
- Custom exception classes for domain-specific errors (e.g., `InferenceError`, `ValidationError`).
- Fail-fast validation at the API boundary using Pydantic.
## Cross-Cutting Concerns (Planned)
- Structured logging (JSON) for easy analysis of inference performance and errors.
- Pydantic for API request/response validation.
- Image quality/format validation before processing.
- JWT-based auth for merchants and B2C users.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
