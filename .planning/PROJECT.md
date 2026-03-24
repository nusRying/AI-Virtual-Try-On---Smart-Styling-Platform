# AI Virtual Try-On + Smart Styling Platform

**Core Value:** Provide highly realistic, diffusion-based virtual try-on that builds consumer trust in online fashion shopping.

**Context:**
The platform addresses the "trust gap" in e-commerce fashion where users cannot visualize how clothes will truly look on them. By combining high-fidelity virtual try-on (VTO) with an "AI Fashion Assistant" (Stylist + Recommendation), the platform moves beyond simple visualization to personalized fashion guidance.

## Requirements

### Validated
- ✓ **Architecture Strategy** — Defined Python (FastAPI) + Next.js + PyTorch stack.
- ✓ **Model Direction** — Selected Diffusion-based VTO (TryOnDiffusion/OpenTryOn) for maximum realism.
- ✓ **Target Niche** — B2B SaaS for e-commerce clothing brands (starting with men's shirts).

### Active
- [ ] **Core VTO Engine** — Implement a diffusion-based inference pipeline for realistic garment overlay.
- [ ] **Pose & Segmentation** — Integrate MediaPipe/OpenPose for body detection and segmentation.
- [ ] **Stylist API** — Basic recommendation logic ("This shirt goes with these pants").
- [ ] **Interactive Loop** — Frontend UI for uploading photos and swapping items.
- [ ] **Merchant Integration** — Basic API/Plugin structure for external stores.

### Out of Scope
- [ ] **Full Outfit Generation** — Initial focus is on single category try-on (tops).
- [ ] **Complex Avatars** — Use real user photos, not 3D avatars.
- [ ] **Real-time Video Try-On** — Focus on high-quality static image generation first.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Diffusion Models | Superior realism compared to GAN-based VITON models; critical for trust. | — Pending Implementation |
| B2B Focus | Faster revenue and lower marketing costs than B2C. | — Pending Implementation |
| FastAPI Backend | Best-in-class performance for AI model orchestration in Python. | — Pending Implementation |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-24 after initialization*
