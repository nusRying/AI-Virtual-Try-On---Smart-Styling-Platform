# Pitfalls Research

**Domain:** AI Virtual Try-On + Smart Styling
**Researched:** 2026-03-24
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Garment/Person Alignment Failures

**What goes wrong:**
The virtual garment looks like a "sticker" placed on top of the person, failing to wrap around the shoulders, arms, or torso correctly. This happens especially in non-standard poses.

**Why it happens:**
Inaccurate pose estimation (MediaPipe) or a lack of dense correspondence between the garment and the person's body. Standard warping (TPS) is often too rigid.

**How to avoid:**
Use **IDM-VTON** or other diffusion-based models that use cross-attention to implicitly learn the "drape" and "wrap" of the fabric. Supplement with **SAM 2** for precise person/garment masking.

**Warning signs:**
"Ghosting" around the edges of the garment, or the garment texture appearing flat while the person's body is at an angle.

**Phase to address:**
Phase 1 (Core VTO Engine).

---

### Pitfall 2: Texture/Logo Distortions

**What goes wrong:**
Brand logos, text, or complex patterns (like plaid) become illegible or "smudged" during the try-on process.

**Why it happens:**
Diffusion models often struggle with text and high-frequency patterns if they aren't properly conditioned on the garment's visual features.

**How to avoid:**
Ensure the VTO model uses a separate **GarmentNet** or **TryOnNet** architecture (like IDM-VTON) that preserves high-resolution features from the original garment image. Use **IP-Adapter** for strong feature conditioning.

**Warning signs:**
Inconsistent patterns across different parts of the garment; "melting" logos.

**Phase to address:**
Phase 1 (Core VTO Engine) & Phase 2 (Advanced VTO).

---

### Pitfall 3: High Inference Latency

**What goes wrong:**
The try-on process takes 30+ seconds, causing high bounce rates for e-commerce users who expect near-instant feedback.

**Why it happens:**
Running full-resolution (1024px) diffusion models is computationally expensive. Large UNets or Transformers (DiT) require significant GPU time.

**How to avoid:**
1. Implement an **Async Worker Pattern** (Celery) with a "loading" state.
2. Provide a **Low-Res Preview** (<2s) using a smaller model or fewer diffusion steps.
3. Optimize with **TensorRT** or **torch.compile**.

**Warning signs:**
Backend timeouts; user drop-off during the "Generating..." state.

**Phase to address:**
Phase 3 (Optimization & Scaling).

---

### Pitfall 4: Background Pollution (Bleeding)

**What goes wrong:**
Parts of the original background or the person's original clothes "bleed" through into the newly generated garment.

**Why it happens:**
Poor segmentation of the original garment or the person's body. The model doesn't know exactly what to overwrite.

**How to avoid:**
Use **SAM 2** (Segment Anything Model 2) for high-precision masking. Ensure the "agnostic" (masked) image used as input to the diffusion model is generated correctly, removing the old garment entirely.

**Warning signs:**
"Halo" effects around the garment; original shirt collar visible behind the new one.

**Phase to address:**
Phase 1 (Core VTO Engine).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| **Synchronous Inference** | Fast to implement; no Redis/Celery needed. | Scalability is zero; API will crash under load. | **PoC only**; never for MVP. |
| **Simple TPS Warping** | Less GPU intensive than diffusion. | Low realism; users won't trust the product. | **Never** for this specific core value. |
| **Generic SDXL Fine-tuning** | Easier than implementing a dedicated VTO architecture. | Poor garment preservation; logos will be ruined. | **Research phase** only. |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **S3 Storage** | Storing images with public-read access. | Use **Presigned URLs** for secure, temporary access to user photos. |
| **Shopify API** | Polking the API for every recommendation request. | **Sync to Vector DB** (Weaviate) periodically and query locally for styling. |
| **GPU Provider** | Relying on a single GPU instance with no failover. | Use a **Managed Worker Pool** (Modal/Replicate) or multi-region instances. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| **VRAM Exhaustion** | "Out of Memory" (OOM) errors on the GPU. | Use **FP16** precision and `attention_slicing`. | 1-5 concurrent requests (depending on GPU). |
| **Redis Queue Congestion** | High latency even when GPUs are idle. | Separate the broker from the result backend; optimize task payload size. | 100+ tasks/sec. |
| **Large Asset Downloads** | Cold starts take 5+ minutes while model weights download. | Use **Persistent Volumes** or bake weights into the Docker image. | Every scale-up event. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| **Silent Failures** | User waits 10s only to see "Error" with no explanation. | Implement **Progress Updates** ("Segmenting...", "Diffusing...") and clear error messages. |
| **Complex Photo Rules** | "Photo must be exactly 512x512 with a white background." | Implement **Auto-Cropping** and background removal in the pipeline. |
| **No "Side-by-Side" view** | Hard for users to compare before/after. | Provide a **Toggle** or "Before/After" slider component. |

## "Looks Done But Isn't" Checklist

- [ ] **Try-On Inference:** Often missing **Background Preservation** — verify background doesn't change when clothes swap.
- [ ] **Pose Estimation:** Often missing **Occlusion Handling** — verify it works if hands are in pockets.
- [ ] **Stylist API:** Often missing **Inventory Awareness** — verify it doesn't recommend out-of-stock items.
- [ ] **Image Upload:** Often missing **EXIF Orientation** — verify portrait photos don't rotate to landscape.

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Alignment Failures | Phase 1 | Qualitative review of 50 varied poses. |
| Logo Distortions | Phase 2 | OCR check on generated brand logos. |
| High Latency | Phase 3 | Load test with 10 concurrent users; target <10s. |
| Background Bleeding | Phase 1 | Binary mask comparison (IoU) on complex backgrounds. |

## Sources

- [IDM-VTON GitHub Issues] — Known artifacts and failures.
- [Virtual Try-On 2024 Benchmarks] — Performance and fidelity traps.
- [FastAPI Deployment Guide] — Latency and scaling pitfalls.

---
*Pitfalls research for: AI Virtual Try-On + Smart Styling Platform*
*Researched: 2026-03-24*
