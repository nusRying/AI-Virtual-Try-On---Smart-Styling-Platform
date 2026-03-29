# Requirements

**Project:** AI Virtual Try-On + Smart Styling Platform
**Version:** v1 (MVP)
**Status:** Defined

## v1 Requirements (Active)

These are the primary requirements for the first version of the platform, focusing on realism and the core API infrastructure.

### Core VTO Engine
- [x] **VTO-01**: **Core Diffusion Pipeline** — Implement IDM-VTON, SAM 2, and MediaPipe for realistic garment overlay and body detection.
- [x] **VTO-02**: **High-Res User Photo Upload** — Support for high-resolution image uploads with validation for size and aspect ratio.

### Smart Styling
- [x] **STYL-01**: **Basic Catalog** — A searchable selection of garments available for try-on (men's shirts focus).
- [x] **STYL-02**: **RAG Recommendations** — Basic "This goes with that" logic using a vector database (Weaviate) for semantic retrieval.

### Platform & Infrastructure
- [x] **PLAT-01**: **Async API Infrastructure** — FastAPI-based gateway with Celery/Redis task queue for managing GPU inference tasks.
- [x] **PLAT-02**: **Merchant Dashboard** — Basic UI for merchants to upload garments and view usage analytics.

## v2 Requirements (Deferred)

These features are valuable but deferred to ensure a focused v1 launch.

- [ ] **STYL-03**: **AI Stylist Chat** — Interactive fashion advice powered by Claude 3.5 Sonnet.
- [ ] **PLAT-03**: **Shopify/Store Plugin** — Direct, one-click integration for e-commerce platforms.
- [ ] **VTO-03**: **Low-Latency Preview** — Fast, low-resolution generation for immediate user feedback.

## Out of Scope (Explicit Exclusions)

- **Full-Body Try-On** — Initial focus is strictly on single category (tops/shirts).
- **3D Avatar Creation** — Focus remains on real user photos for maximum realism and lower friction.
- **Real-Time Video Try-On** — Deferred until temporal consistency in diffusion models is more performant.
- **AI Outfit Generation from Text** — Restricted to curated product catalogs for reliability.

## Traceability

| REQ-ID | Phase | Success Criteria | Status |
|--------|-------|------------------|--------|
| VTO-01 | Phase 1 | System can take a user image and a garment image as input and output a merged try-on image. | Completed |
| VTO-02 | Phase 3 | User can upload a portrait photo through a web form with real-time validation. | Completed |
| STYL-01 | Phase 4 | User can browse a paginated gallery and search items by keywords. | Completed |
| STYL-02 | Phase 5 | User sees "Complete the Look" suggestions generated via semantic retrieval from Weaviate. | Completed |
| PLAT-01 | Phase 2 | API returns a task ID immediately and workers process the pipeline asynchronously. | Completed |
| PLAT-02 | Phase 6 | Merchant can log in, upload new garments, and view "Total Try-Ons" metric. | Completed |

---
*Last updated: 2026-03-24*
