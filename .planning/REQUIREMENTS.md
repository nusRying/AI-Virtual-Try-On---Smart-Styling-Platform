# Requirements

**Project:** AI Virtual Try-On + Smart Styling Platform
**Version:** v1 (MVP)
**Status:** Defined

## v1 Requirements (Active)

These are the primary requirements for the first version of the platform, focusing on realism and the core API infrastructure.

### Core VTO Engine
- [ ] **VTO-01**: **Core Diffusion Pipeline** — Implement IDM-VTON, SAM 2, and MediaPipe for realistic garment overlay and body detection.
- [ ] **VTO-02**: **High-Res User Photo Upload** — Support for high-resolution image uploads with validation for size and aspect ratio.

### Smart Styling
- [ ] **STYL-01**: **Basic Catalog** — A searchable selection of garments available for try-on (men's shirts focus).
- [ ] **STYL-02**: **RAG Recommendations** — Basic "This goes with that" logic using a vector database (Weaviate) for semantic retrieval.

### Platform & Infrastructure
- [ ] **PLAT-01**: **Async API Infrastructure** — FastAPI-based gateway with Celery/Redis task queue for managing GPU inference tasks.
- [ ] **PLAT-02**: **Merchant Dashboard** — Basic UI for merchants to upload garments and view usage analytics.

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
| VTO-01 | | | Pending |
| VTO-02 | | | Pending |
| STYL-01 | | | Pending |
| STYL-02 | | | Pending |
| PLAT-01 | | | Pending |
| PLAT-02 | | | Pending |

---
*Last updated: 2026-03-24*
