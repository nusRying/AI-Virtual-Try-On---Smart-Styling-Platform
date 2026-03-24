# Architecture Research

**Domain:** AI Virtual Try-On + Smart Styling
**Researched:** 2026-03-24
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ UI Comp │  │ Image   │  │ Styling │  │ Auth    │        │
│  │ (Try-On)│  │ Upload  │  │ Chat    │  │ Clerk   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
├───────┴────────────┴────────────┴────────────┴──────────────┤
│                        API Gateway (FastAPI)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    Task Orchestrator (Celery)        │    │
│  └──────────────────────────┬──────────────────────────┘    │
├─────────────────────────────┼───────────────────────────────┤
│                        Inference Layer (GPU)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ IDM-VTON │  │ SAM 2    │  │ MediaPipe│  │ LLM      │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Frontend** | User interface, image cropping/upload, interactive try-on loop. | Next.js 15, Tailwind, React-Query. |
| **API Gateway** | Auth, rate limiting, metadata management, task submission. | FastAPI (Python 3.12+). |
| **Task Queue** | Decoupling API from long-running GPU inference. | Celery + Redis. |
| **Inference Engine** | Running diffusion models, segmentation, and pose estimation. | PyTorch on NVIDIA GPUs (H100/A100). |
| **Vector DB** | Multimodal garment retrieval for styling recommendations. | Weaviate or Pinecone. |
| **Object Storage** | Storing user photos and generated try-on results. | AWS S3 or Google Cloud Storage. |

## Recommended Project Structure

```
root/
├── apps/
│   ├── web/                # Next.js Frontend
│   └── api/                # FastAPI Backend
├── packages/
│   ├── ai-engine/          # Core VTO & Segmentation logic
│   ├── database/           # Prisma/SQLAlchemy schemas
│   └── config/             # Shared ESLint/TSConfig/Tailwind
├── infra/                  # Terraform/Docker compose
└── scripts/                # Model weight download & setup
```

### Structure Rationale

- **Monorepo (Turborepo):** Ideal for managing the tight coupling between the frontend UI and the backend AI schemas.
- **apps/api/:** Keeps the FastAPI code isolated.
- **packages/ai-engine/:** Allows the heavy AI inference logic to be packaged and potentially deployed as separate workers/containers.

## Architectural Patterns

### Pattern 1: Async Worker Pattern

**What:** The API returns a `task_id` immediately, while the GPU worker processes the image in the background.
**When to use:** Any task taking >500ms (VTO inference is 5-10s).
**Trade-offs:** Requires frontend polling or WebSockets; increases infra complexity (Redis/Celery).

**Example:**
```python
# FastAPI Endpoint
@app.post("/try-on")
async def create_try_on(data: TryOnRequest):
    task = run_vto_inference.delay(data.user_img, data.garment_img)
    return {"task_id": task.id}

# Celery Worker
@celery.task
def run_vto_inference(user_img, garment_img):
    result = vto_pipeline(user_img, garment_img)
    return result
```

### Pattern 2: Multimodal RAG (Retrieval Augmented Generation)

**What:** Using visual and text embeddings to find matching clothes for styling.
**When to use:** Powering the "Smart Stylist" or "Complete the Look" features.
**Trade-offs:** Requires maintaining a vector index that stays in sync with the SQL database.

## Data Flow

### Request Flow

```
[User Uploads Photo]
    ↓
[Next.js] → [FastAPI] → [S3 Upload] → [Celery/Redis]
    ↓              ↓           ↓            ↓
[Polling/WS] ← [Inference Done] ← [GPU Worker] ← [S3 Fetch]
```

### Key Data Flows

1. **Try-On Flow:** User uploads photo -> API stores in S3 -> Task queued -> Worker fetches from S3 -> Worker runs IDM-VTON -> Worker uploads result -> API notifies frontend.
2. **Styling Recommendation:** User selects item -> API queries Weaviate for similar/matching items -> LLM (Claude) filters results for "style" -> Frontend displays curated set.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single GPU instance (A10G/L4) for both API and Workers. |
| 1k-100k users | Separate API from GPU Workers. Autoscaling GPU pool based on queue depth. |
| 100k+ users | Multi-region GPU clusters. Edge caching for static garment features. |

### Scaling Priorities

1. **First bottleneck:** GPU VRAM and compute. Solution: Batching requests or using distilled models (OOTDiffusion).
2. **Second bottleneck:** Cold starts for GPU workers. Solution: Persistent worker pool or serverless GPU (Modal/Lambda Labs).

## Anti-Patterns

### Anti-Pattern 1: Synchronous Inference

**What people do:** Waiting for the 10-second diffusion process inside the FastAPI request handler.
**Why it's wrong:** Times out the client, blocks the event loop, and makes horizontal scaling impossible.
**Do this instead:** Use the **Async Worker Pattern** (Celery).

### Anti-Pattern 2: Storing Images in DB

**What people do:** Saving base64 image strings directly in PostgreSQL.
**Why it's wrong:** Bloats the database, slows down queries, and makes CDN integration difficult.
**Do this instead:** Store in **Object Storage (S3)** and only save the URL in the DB.

## Sources

- [FastAPI Best Practices] — Architecture patterns (HIGH confidence)
- [Hugging Face Inference Endpoints] — Scaling GPU workloads (HIGH confidence)
- [Turborepo Documentation] — Monorepo structure (HIGH confidence)

---
*Architecture research for: AI Virtual Try-On + Smart Styling Platform*
*Researched: 2026-03-24*
