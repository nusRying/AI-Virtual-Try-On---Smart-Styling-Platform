# Phase Audit — UI Review

**Audited:** 2026-03-29
**Baseline:** Abstract 6-pillar standards
**Screenshots:** Not captured (no dev server)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Good step-based labels; some generic "Remove" actions. |
| 2. Visuals | 4/4 | High polish, modern dark mode aesthetic, clear focal points. |
| 3. Color | 3/4 | Nice 60/30/10 split but several hardcoded hex/rgba values. |
| 4. Typography | 4/4 | Excellent Inter/Outfit pairing with good hierarchy. |
| 5. Spacing | 3/4 | Radius consistency is good, but margins/gaps are hardcoded and vary. |
| 6. Experience Design | 2/4 | Discrepant hardcoded API URLs; weak empty states for AI suggestions. |

**Overall: 19/24**

---

## Top 3 Priority Fixes

1. **Centralize Backend URL** — Resolve the `localhost` vs `127.0.0.1` discrepancy across components. Use a single source of truth (e.g., `src/config.ts` or `.env`).
2. **Improve Suggestion Empty States** — In `StylingRecommendations.tsx`, replace `return null` with a "Select a garment to see recommendations" message to maintain layout balance.
3. **Tokenize Hardcoded Colors** — Replace hardcoded `rgba(255, 255, 255, 0.02)` and `#000` in component-level CSS with variables from `index.css`.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)
- **Strengths:** Excellent step-by-step guidance for users ("1. Upload Your Photo", "2. Select a Garment"). Action-oriented buttons like "Add to Collection" (Merchant) and "Download Result" (User) are clear.
- **Weaknesses:** "Remove" in `MerchantDashboard.tsx:165` is generic; "Delete Garment" would be more descriptive.
- **Empty States:** `StylingRecommendations.tsx:19` hides the component entirely when empty, which can cause layout shifts when a garment is selected.

### Pillar 2: Visuals (4/4)
- **Hierarchy:** Clear distinction between the setup, catalog, and result panels in `App.tsx`.
- **Polish:** Use of `backdrop-filter: blur(12px)` for the header and `linear-gradient` for branding provides a premium feel.
- **Feedback:** Good use of `cursor: pointer` and hover states (e.g., `scale(1.05)` on garment cards) provides tactile feedback.

### Pillar 3: Color (3/4)
- **Usage:** Follows a strict palette defined in `index.css`.
- **Issues:** Hardcoded colors found:
    - `MerchantDashboard.css:76`: `background: #000;`
    - `MerchantDashboard.css:102`: `rgba(239, 68, 68, 0.1)`
    - `ProductCatalog.css:91`: `background: #000;`
- **Contrast:** High contrast text-to-background ratios in dark mode (Midnight Violet theme).

### Pillar 4: Typography (4/4)
- **Pairing:** 'Inter' for UI/Body and 'Outfit' for Headings is a solid modern choice.
- **Distribution:**
    - `text-transform: uppercase; letter-spacing: 0.05em` used effectively for table headers and sub-labels.
    - Font sizes range from `0.75rem` (hints) to `1.5rem` (main headers), following a logical hierarchy.

### Pillar 5: Spacing (3/4)
- **Consistency:** `var(--radius-lg)` (16px) is consistently used for major containers.
- **Issues:** Gaps and paddings are hardcoded in `rem` without a central scale, leading to slight inconsistencies:
    - `App.css:57`: `gap: 2rem` (Workspace)
    - `MerchantDashboard.css:13`: `gap: 2.5rem` (Dashboard Grid)
    - `ProductCatalog.css:4`: `gap: 1.5rem` (Catalog Container)

### Pillar 6: Experience Design (2/4)
- **API Consistency:** `StylingRecommendations.tsx:17` uses `127.0.0.1` while `App.tsx:9` and others use `localhost`. This can lead to CORS or connectivity issues in certain environments.
- **Loading:** `isUploading` and `isLoading` flags are well-integrated into button `disabled` states and UI overlays.
- **Error Handling:** `App.tsx:235` provides a clear error box with a "Try Again" trigger.
- **UX Gap:** `UserPhotoUpload.tsx:36` only warns about portrait vs landscape after file load. Consider filtering or stronger visual cues in the placeholder.

---

## Files Audited
- `frontend/src/App.tsx`
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/components/MerchantDashboard.tsx`
- `frontend/src/styles/MerchantDashboard.css`
- `frontend/src/components/ProductCatalog.tsx`
- `frontend/src/styles/ProductCatalog.css`
- `frontend/src/components/UserPhotoUpload.tsx`
- `frontend/src/components/StylingRecommendations.tsx`
